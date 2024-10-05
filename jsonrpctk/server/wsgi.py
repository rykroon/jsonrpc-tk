from dataclasses import dataclass, field, InitVar
import json
from typing import Any, Callable

from werkzeug import Request, Response
from werkzeug.exceptions import BadRequest, HTTPException, MethodNotAllowed, UnsupportedMediaType

from jsonrpctk.types import JsonRpcErrorResponse, JsonRpcSuccessResponse
from jsonrpctk.server.methods import MethodDispatcher
from jsonrpctk.server.exception_handlers import ExceptionHandler

@dataclass
class JsonRpcApp:

    methods: InitVar[dict[str, Callable]] = field(default_factory=dict)
    exception_handlers: InitVar[dict[type[Exception], Callable]] = field(default_factory=dict)
    auth_handler: Callable[[Request]] | None = None

    method_dispatcher: MethodDispatcher
    exception_handler: ExceptionHandler

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self._process_http_request(request)
        return response(environ, start_response)

    def __post_init__(self, methods, exception_handlers):
        self.exception_handler = ExceptionHandler(handlers=exception_handlers)
        self.method_dispatcher = MethodDispatcher()
        for name, method in methods.items():
            self.method_dispatcher.add_method(name, method)

    def _process_http_request(self, request: Request) -> Response:    
        if self.auth_handler is not None:
            self.auth_handler(request)

        if request.method != "POST":
            raise MethodNotAllowed(valid_methods=["POST"])

        if not request.is_json:
            raise UnsupportedMediaType

        try:
            request_json = json.loads(request.get_data())
        except json.JSONDecodeError as e:
            raise BadRequest from e

        if isinstance(request_json, list):
            # batch request
            pass

    def _process_jsonrpc_request(
        self, json_payload: Any
    ) -> JsonRpcErrorResponse | JsonRpcSuccessResponse:
        pass
