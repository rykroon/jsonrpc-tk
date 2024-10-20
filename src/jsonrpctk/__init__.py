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


class AttrDict(dict[Any, Any]):

    def __getattr__(self, attr: Any) -> Any:
        try:
            return self[attr]
        except KeyError:
            raise AttributeError

    def __setattr__(self, attr: Any, value: Any) -> None:
        if value is not MISSING:
            self[attr] = value

    def __delitem__(self, attr: Any) -> None:
        del self[attr]


@dataclass(repr=False, eq=False, kw_only=True)
class Request(AttrDict):
    jsonrpc: Literal["2.0"]
    method: str
    params: dict[str, Any] | list[Any] | MissingType = MISSING
    id: int | str | MissingType = MISSING

    def get_params(self) -> dict[str, Any] | list[Any] | None:
        return getattr(self, "params", None)

    def get_id(self) -> int | str | None:
        return getattr(self, "id", None)

    def is_notification(self) -> bool:
        return "id" not in self


class ErrorCode(enum.IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


@dataclass(repr=False, eq=False, kw_only=True)
class Error(AttrDict):
    code: int
    message: str
    data: Any = MISSING

    def get_data(self) -> Any | None:
        return getattr(self, "data", None)


@dataclass(kw_only=True)
class JsonRpcException(Exception):
    code: int
    message: str
    data: Any = None

    def __post_init__(self) -> None:
        super().__init__(self.code, self.message)


@dataclass(repr=False, eq=False, kw_only=True)
class Response(AttrDict):
    jsonrpc: Literal["2.0"]
    result: Any | MissingType = MISSING
    error: JsonRpcError | MissingType = MISSING
    id: int | str | None

    def __post_init__(self) -> None:
        if not self.is_success() and not self.is_error():
            raise TypeError
        
        if self.is_success() and self.is_error():
            raise TypeError()

    def get_result(self) -> Any | None:
        return getattr(self, "result", None)

    def get_error(self) -> Error | None:
        return getattr(self, "error", None)

    def is_success(self) -> bool:
        return "result" in self
    
    def is_error(self) -> bool:
        return "error" in self


# ~~~ Batch ~~~ 

class RequestBatch(list[JsonRpcRequest]):
    pass


class ResponseBatch(list[JsonRpcResponse]):
    pass

