from collections.abc import Mapping, Sequence
from typing import Any, Literal

from jsonrpctk.undefined import Undefined, UndefinedType


class Request(dict):

    def __init__(
        self,
        jsonrpc: Literal["2.0"],
        method: str,
        *,
        params: Mapping[str, Any] | Sequence[Any] | UndefinedType = Undefined,
        id: int | str | UndefinedType = Undefined
    ):
        assert jsonrpc == "2.0", "Invalid json-rpc protocol"
        self["jsonrpc"] = jsonrpc
        self["method"] = method

        if params is not Undefined:
            self["params"] = params

        if id is not Undefined:
            self["id"] = id

    @property
    def jsonrpc(self) -> Literal["2.0"]:
        return self["jsonrpc"]

    @property
    def method(self) -> str:
        return self["method"]

    @property
    def params(self) -> Mapping[str, Any] | Sequence[Any] | None:
        return self.get("params")

    @property
    def id(self) -> int | str | None:
        return self.get("id")

    @property
    def args(self) -> tuple[Any, ...]:
        return tuple(self.params) if isinstance(self.params, Sequence) else ()

    @property
    def kwargs(self) -> dict[str, Any]:
        return dict(self.params) if isinstance(self.params, Mapping) else {}

    def is_notification(self) -> bool:
        return "id" in self
