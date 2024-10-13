from collections.abc import Mapping

from jsonrpctk.errors import Error, JsonRpcException
from jsonrpctk.requests import Request
from jsonrpctk.responses import Response
from jsonrpctk.types import (
    Context,
    ExceptionHandler,
    JsonRpcApp,
)


class ExceptionMiddleware:
    def __init__(
        self,
        app: JsonRpcApp,
        handlers: Mapping[type[Exception] | int, ExceptionHandler] | None = None,
    ):
        self.app = app
        self._code_handlers: dict[int, ExceptionHandler] = {}
        self._exception_handlers: dict[type[Exception], ExceptionHandler] = {}
        if handlers is not None:
            for k, v in handlers.items():
                self.add_handler(k, v)

    def __call__(self, request: Request, context: Context) -> Response | None:
        try:
            return self.app(request, context)

        except Exception as e:
            handler = self.get_handler(e)
            if handler is None:
                raise e

            error = handler(request, context, e)
            return (
                None
                if request.is_notification()
                else Response.from_error(error=error, id=request.id)
            )

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
