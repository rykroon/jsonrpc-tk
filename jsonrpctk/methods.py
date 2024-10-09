from collections.abc import MappingView, Sequence
import inspect
from typing import Any, Callable, ParamSpec

from jsonrpctk.errors import Error, ErrorCode
from jsonrpctk.requests import Request
from jsonrpctk.responses import Response
from jsonrpctk.types import Context


P = ParamSpec("P")


class BaseMethod:
    def __init__(self, method: Callable[P, Any], /, *, name: str | None = None):
        self.method = method
        self.name = name or self.method.__name__

    def call_method(self, request: Request, context: Context) -> Any:
        """
        Should raise a JsonRpcException if the params are invalid.
        """
        raise NotImplementedError

    def __call__(self, request: Request, context: Context) -> Response | None:
        context.setdefault("app", default=self)

        try:
            if request.method != self.name:
                raise Error(
                    code=ErrorCode.METHOD_NOT_FOUND, message="method not found."
                )

            result = self.call_method(request, context)
        except Error as e:
            if context.get("app") is self:
                if request.is_notification():
                    return None

                return Response.new_error(id=request.id, error=e.to_dict())
            raise e

        if request.is_notification():
            return None

        return Response.new_success(id=request.id, result=result)


class Method(BaseMethod):
    def __init__(self, method: Callable[P, Any], /, *, name: str | None = None):
        super().__init__(self, method, name=name)
        self.sig = inspect.Signature.from_callable(self.method)

    def call_method(self, request: Request, context: Context) -> Any:
        try:
            ba = self.sig.bind(*request.args, **request.kwargs)

        except TypeError as e:
            raise Error(code=ErrorCode.INVALID_PARAMS, message=str(e))

        return self.method(*ba.args, **ba.kwargs)


class MethodDispatcher:
    def __init__(self, methods: Sequence[Method] | None = None):
        self._methods = {} if methods is None else {m.name: m for m in methods}

    def __call__(self, request: Request, context: Context) -> Response | None:
        context.setdefault("app", default=self)
        try:
            method = self.get_method(request.method)
            return method(request)

        except Error as e:
            if context.get("app") is self:
                if request.is_notification():
                    return None
                return Response.new_error(id=request.id, error=e.to_dict())
            raise e

    @property
    def methods(self):
        return MappingView(self._methods)

    def add_method(self, method: Method, /) -> None:
        self._methods[method.name] = method

    def get_method(self, name: str) -> Method:
        try:
            return self._methods[name]
        except KeyError:
            raise ErrorCode(
                code=ErrorCode.METHOD_NOT_FOUND, message="method not found."
            )

    def method(
        self, func: Callable[P, Any] | None = None, /, *, name: str | None = None
    ):
        def wrapper(func):
            self.add_method(Method(func, name))
            return func

        if func is None:
            # called as @method()
            return wrapper

        # called as @method
        return wrapper(func)
