from dataclasses import dataclass
from typing import Callable

from jsonrpctk.types import JsonRpcError


ExceptionHandler = Callable[[Exception], JsonRpcError]


@dataclass
class ExceptionHandler:
    handlers: dict[type[Exception], ExceptionHandler]

    def add_handler(self, exc: type[Exception], handler: ExceptionHandler):
        self.handlers[exc] = handler

    def handle_exception(self, exc: Exception) -> JsonRpcError:
        for class_ in exc.__class__.mro()[:-1]:
            if class_ in self.handlers:
                return self.handlers[class_](exc)
        # if we do not find a handler then raise the exception.
        raise exc
