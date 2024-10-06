from dataclasses import dataclass, field, InitVar
import inspect
from typing import Any, Callable, ParamSpec

from jsonrpctk.exceptions import JsonRpcException, JsonRpcErrorCode
from jsonrpctk.types import JsonRpcRequest, JsonRpcResponse
from jsonrpctk.utils import create_success_response


P = ParamSpec("P")


@dataclass(slots=True)
class Method:
    func: Callable[P, Any]
    name: str | None = None
    sig: inspect.Signature = field(init=False)

    def __post_init__(self):
        if self.name is None:
            self.name = self.func.__name__

        self.sig = inspect.Signature.from_callable(self.func)

    def __call__(self, request: JsonRpcRequest) -> JsonRpcResponse | None:
        if request["method"] != self.name:
            raise JsonRpcException(
                code=JsonRpcErrorCode.METHOD_NOT_FOUND, message="method not found."
            )

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

        result = self.func(*ba.args, **ba.kwargs)
        if "id" not in request:
            return None

        return create_success_response(id=request["id"], result=result)


@dataclass(slots=True)
class MethodDispatcher:
    methods: dict[str, Method] = field(default_factory=dict, init=False)

    def __call__(self, request: JsonRpcRequest) -> JsonRpcResponse:
        method = self.get_method(request["method"])
        return method(request)
    
    @classmethod
    def from_list(cls, methods: list[Method]):
        md = cls()
        for method in methods:
            md.add_method(method)
        return md

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
