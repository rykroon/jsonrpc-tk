from dataclasses import dataclass
import enum
from typing import Any, Final, Literal, NotRequired, Self, TypedDict


# ~~~ Type Annotations ~~~

class JsonRpcRequest(TypedDict):
    jsonrpc: Literal["2.0"]
    method: str
    params: NotRequired[dict[str, Any] | list[Any]]
    id: NotRequired[int | str]


class JsonRpcError(TypedDict):
    code: int
    message: str
    data: NotRequired[Any]


class JsonRpcSuccessResponse(TypedDict):
    jsonrpc: Literal["2.0"]
    id: int | str
    result: Any


class JsonRpcErrorResponse(TypedDict):
    jsonrpc: Literal["2.0"]
    id: int | str | None
    error: JsonRpcError


JsonRpcResponse = JsonRpcSuccessResponse | JsonRpcErrorResponse


# ~~~ Concrete Types ~~~

class MissingType:

    def __repr__(self) -> str:
        return "Missing"
    
    def __bool__(self) -> bool:
        return False


MISSING: Final[MissingType] = MissingType()


class Request(dict[str, Any]):

    def __init__(
        self: Self,
        *,
        jsonrpc: Literal["2.0"],
        method: str,
        params: dict[str, Any] | list[Any] | MissingType = MISSING,
        id: int | str | MissingType = MISSING
    ):
        self["jsonrpc"] = jsonrpc
        self["method"] = method

        if params is not MISSING:
            self["params"] = params
        
        if id is not MISSING:
            self["id"] = id

    @property
    def jsonrpc(self) -> Literal["2.0"]:
        return self["jsonrpc"]

    @property
    def method(self) -> str:
        return self["method"]

    def get_params(self) -> dict[str, Any] | list[Any] | None:
        return self.get("params", None)

    def get_id(self) -> int | str | None:
        return self.get("id", None)

    def is_notification(self) -> bool:
        return "id" not in self


class ErrorCode(enum.IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


class Error(dict[str, Any]):

    def __init__(
      self: Self,
      *,
      code: int,
      message: str,
      data: Any | MissingType = MISSING,
    ):
        self["code"] = code
        self["message"] = message

        if data is not MISSING:
            self["data"] = data

    @property
    def code(self) -> int:
        return self["code"]

    @property
    def message(self) -> str:
        return self["message"]

    def get_data(self) -> Any | None:
        return self.get("data", None)


@dataclass(kw_only=True)
class JsonRpcException(Exception):
    code: int
    message: str
    data: Any = None

    def __post_init__(self) -> None:
        super().__init__(self.code, self.message)


class Response(dict[str, Any]):

    def __init__(
        self: Self,
        *,
        jsonrpc: Literal["2.0"],
        result: Any | MissingType = MISSING,
        error: Error | JsonRpcError | MissingType = MISSING,
        id: int | str | None,
    ) -> None:
        if result is MISSING and error is MISSING:
            raise TypeError("Must provide a result or an error.")
        
        if result is not MISSING and error is not MISSING:
            raise TypeError("Cannot provide both a result and an error.")
        
        self["jsonrpc"] = jsonrpc
        self["id"] = id

        if not isinstance(error, MissingType):
            self["error"] = Error(**error)
        else:
            self["result"] = result            

    def get_result(self) -> Any | None:
        return self.get("result", None)

    def get_error(self) -> Error | None:
        return self.get("error", None)

    def is_success(self) -> bool:
        return "result" in self
    
    def is_error(self) -> bool:
        return "error" in self


# ~~~ Batch ~~~ 

class RequestBatch(list[JsonRpcRequest]):
    pass


class ResponseBatch(list[JsonRpcResponse]):
    pass

    def get_by_id(self, id: int | str) -> Response:
        pass

    def count_success(self) -> int:
        pass

    def count_error(self) -> int:
        pass

