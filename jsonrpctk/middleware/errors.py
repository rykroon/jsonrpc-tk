import traceback
from typing import Callable

from jsonrpctk.exceptions import JsonRpcErrorCode
from jsonrpctk.types import (
    Context,
    JsonRpcApp,
    JsonRpcRequest,
    JsonRpcError,
    JsonRpcResponse,
)
from jsonrpctk.utils import create_error


class ServerErrorMiddleware:
    def __init__(
        self,
        app: JsonRpcApp,
        handler: Callable[[JsonRpcRequest, Exception], JsonRpcError] | None = None,
        debug: bool = False,
    ):
        self.app = app
        self.handler = handler
        self.debug = debug

    def __call__(
        self, request: JsonRpcRequest, context: Context
    ) -> JsonRpcResponse | None:
        context.setdefault("app", self)
        try:
            return self.app(request)
        except Exception as e:
            if self.debug is True:
                return self.debug_response(request, context, e)
            elif self.handler is None:
                return self.error_response(request, context, e)
            else:
                return self.handler(request, context, e)

    def debug_response(
        self, request: JsonRpcRequest, context: Context, exc: Exception
    ) -> JsonRpcError:
        return create_error(
            code=JsonRpcErrorCode.INTERNAL_ERROR,
            message=str(exc),
            data={"debug": {"traceback": "".join(traceback.format_exception(exc))}},
        )

    def error_response(
        self, request: JsonRpcRequest, context: Context, exc: Exception
    ) -> JsonRpcError:
        return create_error(
            code=JsonRpcErrorCode.INTERNAL_ERROR, message="Internal Server Error"
        )
