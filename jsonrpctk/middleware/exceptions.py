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
        self._code_handlers: dict[int, ExceptionHandler] = {}
        self._exception_handlers: dict[type[Exception], ExceptionHandler] = {
            JsonRpcException: self.jsonrpc_exception
        }
        if handlers is not None:
            for k, v in handlers.items():
                self.add_handler(k, v)

    def __call__(
        self, request: JsonRpcRequest, context: Context
    ) -> JsonRpcResponse | None:
        context.setdefault("app", self)

        try:
            return self.app(request, context)

        except Exception as e:
            handler = self.get_handler(e)
            if handler is None:
                raise e

            error = handler(request, context, e)
            if "id" not in request:
                return None

            return create_error_response(id=request["id"], error=error)

    def add_handler(self, exc_cls_or_code: type[Exception] | int, handler: ExceptionHandler):
        if isinstance(exc_cls_or_code, int):
            self._code_handlers[exc_cls_or_code] = handler
        else:
            assert issubclass(exc_cls_or_code, Exception)
            self._exception_handlers[exc_cls_or_code] = handler

    def get_handler(self, exc: Exception) -> ExceptionHandler | None:
        if isinstance(exc, JsonRpcException):
            if exc.code in self._code_handlers:
                return self._code_handlers[exc.code]

        for cls in type(exc).mro()[:-1]:
            if cls in self._exception_handlers:
                return self._exception_handlers[cls]

        return None

    def jsonrpc_exception(
        self, request: JsonRpcRequest, context: Context, exc: JsonRpcException
    ) -> JsonRpcError:
        return exc.to_error()
