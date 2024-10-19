from collections.abc import Mapping
from typing import Any, Literal

from jsonrpctk.undefined import Undefined, UndefinedType
from jsonrpctk.errors import Error


class Response(dict):

    def __init__(
        self,
        jsonrpc: Literal["2.0"],
        *,
        result: Any | UndefinedType = Undefined,
        error: Error | dict[str, Any] | UndefinedType = Undefined,
        id: int | str | None,
    ):
        assert jsonrpc == "2.0", "Invalid json-rpc protocol."

        if result is Undefined and error is Undefined:
            raise TypeError("Must specify a result or an error.")

        if result is not Undefined and error is not Undefined:
            raise TypeError("Cannot specify both a result and an error.")

        self["jsonrpc"] = jsonrpc
        self["id"] = id

        if result is not Undefined:
            self["result"] = result

        if error is not Undefined:
            self["error"] = Error(**error) if isinstance(error, Mapping) else error

    @classmethod
    def from_result(cls, result: Any, id: int | str | None):
        return cls(jsonrpc="2.0", result=result, id=id)

    @classmethod
    def from_error(cls, error: Error | Mapping[str, Any], id: int | str | None):
        return cls(jsonrpc="2.0", error=error, id=id)

    @property
    def jsonrpc(self) -> Literal["2.0"]:
        return self["jsonrpc"]

    @property
    def result(self) -> Any | None:
        return self.get("result")

    @property
    def error(self) -> Error | None:
        return self.get("error")

    @property
    def id(self):
        return self["id"]

    def is_success(self) -> bool:
        return "result" in self
    
    def is_error(self) -> bool:
        return "error" in self
