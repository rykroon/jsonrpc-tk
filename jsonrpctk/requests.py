from collections.abc import Mapping, Sequence
import re
from typing import Any, Literal

from jsonrpctk.undefined import Undefined, UndefinedType


INTERNAL_METHOD_REGEX: re.Pattern = re.compile(r"^rpc\.", flags=re.IGNORECASE)


class Request(dict):

    def __init__(
        self,
        jsonrpc: Literal["2.0"],
        method: str,
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
    def jsonrpc(self):
        return self["jsonrpc"]

    @property
    def method(self):
        return self["method"]

    @property
    def params(self):
        return self.get("params", Undefined)

    @property
    def id(self):
        return self.get("id", Undefined)

    @property
    def args(self) -> tuple[Any, ...]:
        return tuple(self.params) if isinstance(self.params, Sequence) else ()

    @property
    def kwargs(self) -> dict[str, Any]:
        return dict(self.params) if isinstance(self.params, Mapping) else {}

    def is_notification(self) -> bool:
        return self.id is Undefined
