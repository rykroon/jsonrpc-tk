from dataclasses import dataclass, field
from typing import Any, Callable, ParamSpec

from pydantic import validate_call

from jsonrpctk.exceptions import JsonRpcException
from jsonrpctk.types import JsonRpcErrorCode


P = ParamSpec("P")


@dataclass
class MethodDispatcher:
    methods: dict[str, Callable[P, Any]] = field(init=False)

    def add_method(self, name: str, method: Callable[P, Any]):
        self.methods[name] = validate_call(method)

    def get_method(self, name: str):
        try:
            return self.methods[name]
        except KeyError:
            raise JsonRpcException(
                code=JsonRpcErrorCode.METHOD_NOT_FOUND,
                message="The method does not exist",
            )
