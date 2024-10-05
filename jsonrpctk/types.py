from typing import Any, Callable, Literal, NotRequired, TypedDict


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
JsonRpcApp = Callable[[JsonRpcRequest], JsonRpcResponse]
