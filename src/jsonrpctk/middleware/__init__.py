from typing import ParamSpec, Protocol
from jsonrpctk.types import Context, JsonRpcApp, JsonRpcRequest, JsonRpcResponse


P = ParamSpec("P")


class MiddlewareClass(Protocol[P]):
    def __init__(self, app: JsonRpcApp, *args: P.args, **kwargs: P.kwargs): ...

    def __call__(
        self, request: JsonRpcRequest, context: Context
    ) -> JsonRpcResponse | None: ...


class Middleware:
    def __init__(
        self, cls: type[MiddlewareClass[P]], *args: P.args, **kwargs: P.kwargs
    ):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs
