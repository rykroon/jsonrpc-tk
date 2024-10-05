from dataclasses import dataclass
from typing import Any, Callable

from jsonrpctk.exceptions import JsonRpcException, JsonRpcErrorCode
from jsonrpctk.types import (
    JsonRpcApp, JsonRpcError, JsonRpcRequest, JsonRpcResponse
)
from jsonrpctk.utils import create_error, create_error_response


ExceptionHandler = Callable[[JsonRpcRequest, Exception], JsonRpcError]


@dataclass(slots=True)
class ExceptionMiddleware:
    app: JsonRpcApp
    handlers: dict[type[Exception], ExceptionHandler]

    def __call__(self, request: JsonRpcRequest) -> JsonRpcResponse:
        try:
            return self.app(request)
        except Exception as e:
            handler = self.get_handler(e)
            error = handler(request, e)
            return create_error_response(id=request["id"], error=error)

    def add_handler(self, exc_cls: type[Exception], handler: ExceptionHandler):
        self.handlers[exc_cls] = handler

    def get_handler(self, exc: Exception):
        for cls in type(exc).mro()[:-1]:
            if cls in self.handlers:
                return self.handlers[cls]
        raise exc


def jsonrpc_exception_handler(request: JsonRpcRequest, exc: JsonRpcException) -> JsonRpcError:
    return exc.to_error()


def exception_handler(request: JsonRpcRequest, ex: Exception) -> JsonRpcError:
    return create_error(code=JsonRpcErrorCode.INTERNAL_ERROR, message="Internal Server Error")
