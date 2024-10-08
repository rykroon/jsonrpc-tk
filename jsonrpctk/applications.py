from collections.abc import Mapping, Sequence
from typing import Any

from jsonrpctk.middleware import Middleware
from jsonrpctk.middleware.errors import ServerErrorMiddleware
from jsonrpctk.middleware.exceptions import ExceptionMiddleware
from jsonrpctk.methods import MethodDispatcher, Method
from jsonrpctk.types import (
    ExceptionHandler,
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcApp,
)


class JsonRpcServer:
    def __init__(
        self,
        methods: Sequence[Method] | None = None,
        exception_handlers: Mapping[type[Exception] | int, ExceptionHandler] = None,
        debug: bool = False,
    ):
        self.method_dispatcher = MethodDispatcher(methods)
        self.exception_handlers = (
            {} if exception_handlers is None else dict(exception_handlers)
        )
        self.debug = debug
        self.middleware_stack: JsonRpcApp | None = None

    def __call__(
        self, request: JsonRpcRequest, context: dict[Any, Any]
    ) -> JsonRpcResponse | None:
        context.setdefault("app", self)
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()

        return self.middleware_stack(request)

    def build_middleware_stack(self) -> JsonRpcApp:
        error_handler = None
        exception_handlers = {}

        for key, value in self.exception_handlers.items():
            if key == Exception:
                error_handler = value
            else:
                exception_handlers[key] = value

        middleware = (
            Middleware(ServerErrorMiddleware, handler=error_handler, debug=self.debug),
            Middleware(ExceptionMiddleware, handlers=exception_handlers),
        )

        app = self.method_dispatcher

        for mw in reversed(middleware):
            app = mw.cls(app, *mw.args, **mw.kwargs)

        return app
