from collections.abc import Mapping

from jsonrpctk.exceptions import JsonRpcException
from jsonrpctk.types import (
    Context,
    ExceptionHandler,
    JsonRpcApp,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcResponse,
)
from jsonrpctk.utils import create_error_response


class ExceptionMiddleware:
    def __init__(
        self,
        app: JsonRpcApp,
        handlers: Mapping[type[Exception] | int, ExceptionHandler] | None = None,
    ):
        self.app = app
        self.handlers = {} if handlers is None else dict(handlers)

        if JsonRpcException not in self.handlers:
            self.handlers[JsonRpcException] = self.jsonrpc_exception

    def __call__(
        self, request: JsonRpcRequest, context: Context
    ) -> JsonRpcResponse | None:
        context.setdefault("app", self)
        try:
            return self.app(request, context)

        except Exception as e:
            handler = self.get_handler(e)
            error = handler(request, context, e)
            if "id" not in request:
                return None
            return create_error_response(id=request["id"], error=error)

    def add_handler(self, exc_cls: type[Exception], handler: ExceptionHandler):
        self.handlers[exc_cls] = handler

    def get_handler(self, exc: Exception):
        if isinstance(exc, JsonRpcException):
            if exc.code in self.handlers:
                return self.handlers[exc.code]

        for cls in type(exc).mro()[:-1]:
            if cls in self.handlers:
                return self.handlers[cls]

        raise exc

    def jsonrpc_exception(
        self, request: JsonRpcRequest, context: Context, exc: JsonRpcException
    ) -> JsonRpcError:
        return exc.to_error()
