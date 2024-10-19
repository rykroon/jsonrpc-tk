from dataclasses import dataclass
import enum
from typing import Any

from jsonrpctk.undefined import Undefined, UndefinedType


class ErrorCode(enum.IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


class Error(dict):

    def __init__(
        self,
        code: int,
        message: str,
        *,
        data: Any | UndefinedType = Undefined
    ):
        self["code"] = code
        self["message"] = message
        if data is not Undefined:
            self["data"] = data

    @property
    def code(self) -> int:
        return self["code"]

    @property
    def message(self) -> str:
        return self["message"]

    @property
    def data(self) -> Any:
        return self.get("data")

    def to_exception(self) -> 'JsonRpcException':
        return JsonRpcException(code=self.code, message=self.message, data=self.data)


@dataclass(kw_only=True)
class JsonRpcException(Exception):
    code: int
    message: str
    data: Any | UndefinedType = Undefined

    def __post_init__(self):
        super().__init__(self.code, self.message)

    def to_error(self) -> Error:
        return Error(
            code=self.code,
            message=self.message,
            data=self.data # check this out later.
        )
