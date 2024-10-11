import enum
from typing import Any

from jsonrpctk.undefined import Undefined, UndefinedType


class ErrorCode(enum.IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


class Error(Exception):
    code: int
    message: str
    data: Any | UndefinedType = Undefined

    def __init__(self, code: int, message: str, data: Any | UndefinedType = Undefined):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.code, self.message)

    @classmethod
    def from_dict(cls, error: dict[str, Any]):
        return cls(**error)

    def to_dict(self):
        if self.data is Undefined:
            return {"code": self.code, "message": self.message}
        return {"code": self.code, "message": self.message, "data": self.data}
