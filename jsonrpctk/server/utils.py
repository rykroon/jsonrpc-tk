from typing import Any
from pydantic import TypeAdapter, ValidationError
from jsonrpctk.types import JsonRpcRequest, JsonRpcErrorCode
from jsonrpctk.exceptions import JsonRpcError


ta = TypeAdapter(JsonRpcRequest)


def parse_json_payload(payload: dict[Any, Any]) -> JsonRpcRequest:
    try:
        ta.validate_python(payload)
    except ValidationError as e:
        e.errors()
        raise JsonRpcError(
            code=JsonRpcErrorCode.INVALID_PARAMS,
            message="invalid method parameter(s)."
        )
