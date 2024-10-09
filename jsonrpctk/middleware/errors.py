import traceback
from typing import Callable

from jsonrpctk.errors import Error, ErrorCode
from jsonrpctk.requests import Request
from jsonrpctk.responses import Response
from jsonrpctk.types import Context, JsonRpcApp
from jsonrpctk.utils import create_error


class ServerErrorMiddleware:
    def __init__(
        self,
        app: JsonRpcApp,
        handler: Callable[[Request, Exception], Error] | None = None,
        debug: bool = False,
    ):
        self.app = app
        self.handler = handler
        self.debug = debug

    def __call__(self, request: Request, context: Context) -> Response | None:
        context.setdefault("app", self)

        try:
            return self.app(request, context)

        except Exception as e:
            if self.debug is True:
                error = self.debug_response(request, context, e)
            elif self.handler is None:
                error = self.error_response(request, context, e)
            else:
                error = self.handler(request, context, e)
            
            if request.is_notification():
                return None

            return Response.new_error(id=request.id, error=error)

    def debug_response(
        self, request: Request, context: Context, exc: Exception
    ) -> Error:
        return Error(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(exc),
            data={"debug": {"traceback": "".join(traceback.format_exception(exc))}},
        )

    def error_response(
        self, request: Request, context: Context, exc: Exception
    ) -> Error:
        return create_error(
            code=ErrorCode.INTERNAL_ERROR, message="Internal Server Error"
        )
