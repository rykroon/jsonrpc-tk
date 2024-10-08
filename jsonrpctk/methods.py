from collections.abc import Sequence
import inspect
from typing import Any, Callable, ParamSpec

from jsonrpctk.exceptions import JsonRpcException, JsonRpcErrorCode
from jsonrpctk.types import Context, JsonRpcRequest, JsonRpcResponse
from jsonrpctk.utils import create_success_response


P = ParamSpec("P")


class BaseMethod:
    def __init__(self, method: Callable[P, Any], /, *, name: str | None = None):
        self.method = method
        self.name = name or self.method.__name__

    def call_method(self, request: JsonRpcRequest, context: Context) -> Any:
        """
        Should raise a JsonRpcException if the params are invalid.
        """
        raise NotImplementedError

    def __call__(
        self, request: JsonRpcRequest, context: Context
    ) -> JsonRpcResponse | None:
        context.setdefault("app", default=self)

        if request["method"] != self.name:
            raise JsonRpcException(
                code=JsonRpcErrorCode.METHOD_NOT_FOUND, message="method not found."
            )

        result = self.call_method(request, context)
        if "id" not in request:
            return None

        return create_success_response(id=request["id"], result=result)


class Method(BaseMethod):
    def __init__(self, method: Callable[P, Any], /, *, name: str | None = None):
        super().__init__(self, method, name=name)
        self.sig = inspect.Signature.from_callable(self.method)

    def call_method(self, request: JsonRpcRequest, context: Context) -> Any:
        params = request.get("params", None)

        try:
            if isinstance(params, dict):
                ba = self.sig.bind(**params)
            elif isinstance(params, list):
                ba = self.sig.bind(*params)
            elif params is None:
                ba = self.sig.bind()

        except TypeError as e:
            raise JsonRpcException(code=JsonRpcErrorCode.INVALID_PARAMS, message=str(e))

        return self.method(*ba.args, **ba.kwargs)


class MethodDispatcher:
    def __init__(self, methods: Sequence[Method] | None = None):
        self.methods = {} if methods is None else {m.name: m for m in methods}

    def __call__(self, request: JsonRpcRequest, context: Context) -> JsonRpcResponse:
        context.setdefault("app", default=self)
        method = self.get_method(request["method"])
        return method(request)

    def add_method(self, method: Method, /) -> None:
        self.methods[method.name] = method

    def get_method(self, name: str) -> Method:
        try:
            return self.methods[name]
        except KeyError:
            raise JsonRpcException(
                code=JsonRpcErrorCode.METHOD_NOT_FOUND, message="method not found."
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
