from dataclasses import dataclass, field
import inspect
from typing import Any, Callable, ParamSpec, Self, TypeVar

from jsonrpctk.errors import Error, ErrorCode, JsonRpcException
from jsonrpctk.requests import Request
from jsonrpctk.responses import Response
from jsonrpctk.types import Context


P = ParamSpec("P")
T = TypeVar("T")

PrepareArgsType = Callable[[Request, Context], tuple[tuple[Any, ...], dict[str, Any]]]


def _default_prepare_args(
    request: Request, context: Context
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    return request.args, request.kwargs


@dataclass(kw_only=True)
class Method:
    function: Callable[P, T]
    name: str | None = None
    prepare_args: PrepareArgsType = field(
        repr=False, compare=False, default=_default_prepare_args
    )
    signature: inspect.Signature = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        if self.name is None:
            self.name = self.function.__name__
        self.signature = inspect.Signature.from_callable(self.function)

    def __init__(
        self: Self,
        func: Callable[P, T],
        /, *,
        name: str | None = None,
        prepare_args: PrepareArgsType | None = None,
    ):
        self.func = func
        self.name = name or func.__name__
        self.prepare_args = prepare_args or _default_prepare_args
        self.sig = inspect.Signature.from_callable(self.func)

    def __call__(self: Self, request: Request, context: Context) -> Response | None:
        if request.method != self.name:
            if request.is_notification():
                return None

            error = Error(
                code=ErrorCode.METHOD_NOT_FOUND,
                message=f"Method '{request.method}' not found."
            )
            return Response.from_error(error=error, id=request.id)

        try:
            return self.handle(request, context)

        except JsonRpcException as exc:
            if request.is_notification():
                return None
            return Response.from_error(error=exc.to_error(), id=request.id)

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


@dataclass(kw_only=True)
class Namespace:

    name: str
    separator: str = "."
    methods:dict[str, Method] = field(init=False, repr=False, default_factory=dict)

    def __call__(self: Self, request: Request, context: Context) -> Response | None:
        if request.method not in self.methods:
            if request.is_notification():
                return None

            error = Error(
                code=ErrorCode.METHOD_NOT_FOUND,
                message=f"Method '{request.method}' not found."
            )
            return Response.from_error(error=error, id=request.id)

        method = self.methods[request.method]

        try:
            return method.handle(request, context)
        except JsonRpcException as e:
            if request.is_notification():
                return None
            
            return Response.from_error(error=e.to_error(), id=request.id)

    def add_method(self: Self, method: Method):
        key = self.name + self.sep + method.name
        self.methods[key] = method

    def get_method(self: Self, name: str) -> Method:
        try:
            return self.methods[name]
        except KeyError:
            raise JsonRpcException(
                code=ErrorCode.METHOD_NOT_FOUND, message=f"Method '{name}' not found."
            )

    def register(
        self: Self,
        func: Callable[P, T] | None = None,
        /, *,
        name: str | None = None,
        prepare_args: PrepareArgsType | None = None
    ):
        def wrapper(func: Callable[P, T]) -> Callable[P, T]:
            method = Method(function=func, name=name, prepare_args=prepare_args)
            self.add_method(method)
            return func

        if func is None:
            # called as @method()
            return wrapper

        # called as @method
        return wrapper(func)
