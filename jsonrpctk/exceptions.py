from dataclasses import dataclass
import enum
from typing import Any

from jsonrpctk.types import JsonRpcError
from jsonrpctk.utils import create_error


class JsonRpcErrorCode(enum.IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


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
