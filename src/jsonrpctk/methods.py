from collections.abc import Sequence
import inspect
from typing import Any, Callable, ParamSpec, Self, TypeVar

from jsonrpctk.errors import Error, ErrorCode, JsonRpcException
from jsonrpctk.requests import Request
from jsonrpctk.responses import Response
from jsonrpctk.types import Context


P = ParamSpec("P")
T = TypeVar("T")


def _default_prepare_args(
    request: Request, context: Context
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    return request.args, request.kwargs


class Method:

    def __init__(
        self: Self,
        func: Callable[P, T],
        /, *,
        name: str | None = None,
        prepare_args: Callable[[Request, Context], tuple[tuple[Any, ...], dict[str, Any]]] | None = None,
    ):
        self.func = func
        self.name = name or func.__name__
        self.prepare_args = prepare_args or _default_prepare_args
        self.sig = inspect.Signature.from_callable(self.func)

    def __call__(self: Self, request: Request, context: Context) -> Response | None:
        if request.method != self.name:
            if request.is_notification():
                return None
            error = Error(code=ErrorCode.METHOD_NOT_FOUND, message=f"Method '{request.method}' not found.")
            return Response.from_error(error=error, id=request.id)

        try:
            return self.handle(request, context)
        
        except JsonRpcException as e:
            if request.is_notification():
                return None
            return Response.from_error(error=e.to_error(), id=request.id)
        
    def __eq__(self, other):
        return (
            isinstance(other, Method)
            and other.name == self.name
        )

    def handle(self: Self, request: Request, context: Context) -> Response | None:
        args, kwargs = self.prepare_args(request, context)

        try:
            ba = self.sig.bind(*args, **kwargs)

        except TypeError as e:
            raise JsonRpcException(code=ErrorCode.INVALID_PARAMS, message=str(e))

        result = self.func(*ba.args, **ba.kwargs)
        if request.is_notification():
            return None

        return Response.from_result(result=result, id=request.id)

    def __repr__(self):
        return f"{self.name}({", ".join([str(p) for p in self.sig.parameters.values()])})"


class Namespace:

    def __init__(
        self,
        name: str, 
        /,
        *,
        sep: str = ".",
        methods: Sequence[Method] | None = None,
    ):
        self.name = name
        self.sep = sep
        self.dispatcher = MethodDispatcher()
        for method in methods:
            self.add_method(method)

    def __call__(self: Self, request: Request, context: Context) -> Response | None:
        return self.dispatcher(request, context)

    def __eq__(self: Self, other: Any):
        return (
            isinstance(other, Namespace)
            and self.name == other.name
        )

    @property
    def prefix(self) -> str:
        return self.name + self.sep
    
    @property
    def methods(self) -> dict[str, Method]:
        return self.dispatcher.methods

    def add_method(self: Self, method: Method, /, name: str | None = None):
        name = method.name if name is None else name
        name = self.prefix + name
        self.dispatcher.add_method(method, name=name)

    def get_method(self: Self, name: str) -> Method | None:
        return self.dispatcher.get_method(name)


class MethodDispatcher:

    def __init__(
        self,
        *,
        methods: Sequence[Method] | None = None,
        namespaces: Sequence[Namespace] | None = None
    ):
        self.methods = {}
        if methods is not None:
            for method in methods:
                self.add_method(method)

        if namespaces is not None:
            for namespace in namespaces:
                self.add_namespace(namespace)

    def __call__(self, request: Request, context: Context) -> Response | None:
        method = self.get_method(request.method)
        return method(request, context)

    def add_method(self, method: Method, /, *, name: str | None = None) -> None:
        key = method.name if name is None else name
        self.methods[key] = method

    def add_namespace(self, namespace: Namespace, /) -> None:
        self.methods.update(namespace.methods)

    def get_method(self, name: str) -> Method:
        try:
            return self.methods[name]
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
