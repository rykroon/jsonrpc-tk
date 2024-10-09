from dataclasses import dataclass, asdict
from typing import Any, Literal

from jsonrpctk.undefined import Undefined, UndefinedType, _omit_undefined
from jsonrpctk.errors import Error


@dataclass(kw_only=True, slots=True)
class Response:
    jsonrpc: Literal["2.0"] = "2.0"
    result: Any | UndefinedType = Undefined
    error: Error | UndefinedType = Undefined
    id: int | str | None

    def __post_init__(self):
        if self.result is Undefined and self.error is Undefined:
            raise TypeError("Must specify a result or an error.")

        if self.result is not Undefined and self.error is not Undefined:
            raise TypeError("Cannot specify both a result and an error.")
    
    @classmethod
    def new_success(cls, result: Any, id: int | str | None):
        return cls(result=result, id=id)

    @classmethod
    def new_error(cls, error: Any, id: int | str | None):
        return cls(error=error, id=id)

    def to_dict(self):
        return asdict(self, dict_factory=_omit_undefined)
