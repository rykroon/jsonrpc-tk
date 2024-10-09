from collections.abc import Mapping, Sequence
from dataclasses import dataclass, asdict
from typing import Any, Literal

from jsonrpctk.undefined import Undefined, UndefinedType, _omit_undefined


@dataclass(kw_only=True, slots=True)
class Request:
    jsonrpc: Literal["2.0"]
    method: str
    id: str | int | UndefinedType = Undefined
    params: Mapping[str, Any] | Sequence[Any] | UndefinedType = Undefined

    @classmethod
    def from_dict(cls, payload: dict[str, Any]):
        return cls(**payload)

    @property
    def args(self) -> tuple[Any, ...]:
        return tuple(self.params) if isinstance(self.params, Sequence) else ()

    @property
    def kwargs(self) -> dict[str, Any]:
        return dict(self.params) if isinstance(self.params, Mapping) else {}

    def is_notification(self) -> bool:
        return self.id is Undefined

    def to_dict(self):
        return asdict(self, dict_factory=_omit_undefined)
