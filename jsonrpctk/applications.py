from collections.abc import Mapping, Sequence

from jsonrpctk.middleware.exceptions import ExceptionMiddleware
from jsonrpctk.methods import MethodDispatcher, Method
from jsonrpctk.types import JsonRpcRequest, JsonRpcResponse, JsonRpcApp


class JsonRpcServer:
    def __init__(self, methods: Sequence[Method] | None = None):
        self.method_dispatcher = MethodDispatcher(methods)
        self.middleware_stack: JsonRpcApp | None = None
    
    def __call__(self, request: JsonRpcRequest) -> JsonRpcResponse | None:
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()

        return self.middleware_stack(request)

    def build_middleware_stack(self) -> JsonRpcApp:
        pass
