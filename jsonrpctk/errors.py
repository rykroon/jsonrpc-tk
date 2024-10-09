from dataclasses import dataclass, asdict
import enum
from typing import Any

from jsonrpctk.undefined import Undefined, UndefinedType, _omit_undefined


class ErrorCode(enum.IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


@dataclass(kw_only=True)
class Error(Exception):
    code: int
    message: str
    data: Any | UndefinedType = Undefined

    def __post_init__(self):
        super().__init__(self.code, self.message)

    @classmethod
    def from_dict(cls, error: dict[str, Any]):
        return cls(**error)

    def to_dict(self):
        return asdict(self, dict_factory=_omit_undefined)
