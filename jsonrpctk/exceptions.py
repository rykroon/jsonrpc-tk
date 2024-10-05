from dataclasses import dataclass
from typing import Any

from jsonrpctk.types import JsonRpcError, JsonRpcErrorCode, create_error


@dataclass
class JsonRpcException(Exception):
    code: int
    message: str
    data: Any = None

    def __post_init__(self):
        super().__init__(self.code, self.message)

    @classmethod
    def from_error(cls, error: JsonRpcError):
        return cls(**error)

    def to_error(self) -> JsonRpcError:
        return create_error(self.code, self.message, self.data)


@dataclass
class MethodNotFound(JsonRpcException):
    method_name: str
    code: int = JsonRpcErrorCode.METHOD_NOT_FOUND,
    message: str = "The method does not exist."
    data: Any = None


@dataclass
class InvalidParams(JsonRpcException):
    code: int = JsonRpcErrorCode.INVALID_PARAMS
    message: str = "Invalid method parameter(s)."
    data: Any = None

