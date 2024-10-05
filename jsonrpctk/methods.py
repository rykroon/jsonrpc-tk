from dataclasses import dataclass, field
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

    def __pos_init__(self):
        if self.name is None:
            self.name = self.func.__name__

        self.sig = inspect.Signature(self.func)

    def __call__(self, request: JsonRpcRequest) -> JsonRpcResponse:
        assert request["method"] == self.name
        params = request.get("params", None)

        try:
            if isinstance(params, dict):
                ba = self.sig.bind(**params)
            elif isinstance(params, list):
                ba = self.sig.bind(*params)
            elif params is None:
                ba = self.sig.bind()

        except TypeError as e:
            raise JsonRpcException(
                code=JsonRpcErrorCode.INVALID_PARAMS,
                message=str(e)
            )

        result = self.func(*ba.args, **ba.kwargs)
        return create_success_response(id=request["id"], result=result)


@dataclass(slots=True)
class MethodDispatcher:
    methods: dict[str, Method] = field(default_factory=dict)

    def __call__(self, request: JsonRpcRequest) -> JsonRpcResponse:
        method = self.get_method(request["method"])
        return method(request)

    def add_method(self, func: Callable[P, Any], name: str | None = None) -> None:
        method = Method(func, name)
        self.methods[method.name] = method

    def get_method(self, name: str) -> Method:
        try:
            return self.methods[name]
        except KeyError:
            raise JsonRpcException(
                code=JsonRpcErrorCode.METHOD_NOT_FOUND,
                message="method not found."
            )
