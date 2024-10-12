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
            self["error"] = Error(**error) if isinstance(error, dict) else error

    @classmethod
    def from_result(cls, result: Any, id: int | str | None):
        return cls(jsonrpc="2.0", id=id, result=result)

    @classmethod
    def from_error(cls, error: Any, id: int | str | None):
        return cls(jsonrpc="2.0", id=id, error=error)

    @property
    def jsonrpc(self):
        return self["jsonrpc"]

    @property
    def result(self):
        return self.get("result", Undefined)

    @property
    def error(self):
        return self.get("error", Undefined)

    @property
    def id(self):
        return self["id"]
