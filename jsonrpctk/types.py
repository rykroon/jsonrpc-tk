import enum
from typing import Any, Literal, NotRequired, TypedDict


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


class JsonRpcErrorCode(enum.IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


def create_request(
    method: str,
    id: int | str | None = None,
    params: dict[str, Any] | list[Any] | None = None,
) -> JsonRpcRequest:
    request = {"jsonrpc": "2.0", "method": method}
    if id is not None:
        request["id"] = id

    if params is not None:
        request["params"] = params

    return request


def create_error(code: int, message: str, data: Any = None) -> JsonRpcError:
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data

    return error


def create_success_response(id: int | str, result: Any) -> JsonRpcSuccessResponse:
    return {"jsonrpc": "2.0", "id": id, "result": result}


def create_error_response(
    id: int | str | None, error: JsonRpcError
) -> JsonRpcErrorResponse:
    return {"jsonrpc": "2.0", "id": id, "error": error}
