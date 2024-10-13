from collections.abc import Sequence
import inspect
from typing import Any, Callable, ParamSpec, TypeVar

from jsonrpctk.errors import Error, ErrorCode, JsonRpcException
from jsonrpctk.requests import Request
from jsonrpctk.responses import Response
from jsonrpctk.types import Context


P = ParamSpec("P")
T = TypeVar["T"]


class Method:

    def __init__(self, func: Callable[P, T], /, *, name: str | None = None):
        self.func = func
        self.name = name or func.__name__
        self.sig = inspect.Signature.from_callable(self.func)

    def __call__(self, request: Request, context: Context) -> Response | None:
        if request.method != self.name:
            raise JsonRpcException(
                code=ErrorCode.METHOD_NOT_FOUND,
                message=f"Method '{request.method}' was not found."
            )

        try:
            ba = self.sig.bind(*request.args, **request.kwargs)

        except TypeError as e:
            raise JsonRpcException(code=ErrorCode.INVALID_PARAMS, message=str(e))

        result = self.func(*ba.args, **ba.kwargs)
        if request.is_notification():
            return None

        return Response.from_result(result=result, id=request.id)


class MethodDispatcher:

    def __init__(self, methods: Sequence[Method] | None = None):
        self._methods = {} if methods is None else {m.name: m for m in methods}

    def __call__(self, request: Request, context: Context) -> Response | None:
        method = self.get_method(request.method)
        return method(request, context)

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
        self, func: Callable[P, T] | None = None, /, *, name: str | None = None
    ):
        def wrapper(func):
            self.add_method(Method(func=func, name=name))
            return func

        if func is None:
            # called as @method()
            return wrapper

        # called as @method
        return wrapper(func)
