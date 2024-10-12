from collections.abc import Sequence
import inspect
from typing import Any, Callable, ParamSpec

from jsonrpctk.errors import Error, ErrorCode, JsonRpcException
from jsonrpctk.requests import Request
from jsonrpctk.responses import Response
from jsonrpctk.types import Context


P = ParamSpec("P")


class Method:

    def __init__(self, func: Callable[P, Any], /, *, name: str | None = None):
        self.func = func
        self.name = name or func.__name__
        self.sig = inspect.Signature.from_callable(self.func)

    def __call__(self, request: Request, context: Context) -> Response | None:
        context.setdefault("app", self)

        if request.method != self.name:
            error = Error(
                code=ErrorCode.METHOD_NOT_FOUND,
                message=f"Method '{request.method}' not found."
            )
            self._handle_error(request, context, error)

        try:
            ba = self.sig.bind(*request.args, **request.kwargs)

        except TypeError as e:
            error = Error(code=ErrorCode.INVALID_PARAMS, message=str(e))
            return self._handle_error(request, context, error)

        try:
            result = self.func(*ba.args, **ba.kwargs)

        except JsonRpcException as e:
            return self._handle_error(request, context, e)

        return (
            None
            if request.is_notification()
            else Response.from_result(result=result, id=request.id)
        )

    def _handle_error(self, request: Request, context: Context, error: Error) -> Response | None:
        """
            If the main app is this object (self), then return a Response,
            otherwise raise the error and allow it to be handled up the stack.
        """
        if context.get("app") is self:
            return (
                None
                if request.is_notification()
                else Response.from_error(error=error, id=request.id)
            )

        raise error.to_exception()


class MethodDispatcher:

    def __init__(self, methods: Sequence[Method] | None = None):
        self._methods = {} if methods is None else {m.name: m for m in methods}

    def __call__(self, request: Request, context: Context) -> Response | None:
        context.setdefault("app", self)
        try:
            method = self.get_method(request.method)
            return method(request, context)

        except JsonRpcException as e:
            if context.get("app") is self:
                if request.is_notification():
                    return None
                return Response.from_error(id=request.id, error=e)
            raise e

    @property
    def method_names(self) -> tuple[str, ...]:
        return tuple(m.name for m in self._methods.values())

    def add_method(self, method: Method, /) -> None:
        self._methods[method.name] = method

    def get_method(self, name: str) -> Method:
        try:
            return self._methods[name]
        except KeyError:
            raise JsonRpcException(
                code=ErrorCode.METHOD_NOT_FOUND, message=f"Method '{name}' not found."
            )

    def register(
        self, func: Callable[P, Any] | None = None, /, *, name: str | None = None
    ):
        def wrapper(func):
            self.add_method(Method(func=func, name=name))
            return func

        if func is None:
            # called as @method()
            return wrapper

        # called as @method
        return wrapper(func)
