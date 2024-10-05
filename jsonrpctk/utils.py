
from typing import Any
from jsonrpctk.types import (
    JsonRpcRequest, JsonRpcError,JsonRpcErrorResponse, JsonRpcSuccessResponse
)


def create_request(
    method: str,
    id: int | str,
    params: dict[str, Any] | list[Any] | None = None,
) -> JsonRpcRequest:
    request = {"jsonrpc": "2.0", "method": method, "id": id}
    if params is not None:
        request["params"] = params
    return request


def create_notification(
    method: str, params: dict[str, Any] | list[Any] | None = None
) -> JsonRpcRequest:
    request = {"jsonrpc": "2.0", "method": method}
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