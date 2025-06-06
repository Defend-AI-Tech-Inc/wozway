

from datetime import datetime
from enum import Enum
from email.message import Message
import os
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from httpx import Response
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from ..types.basemodel import Unset

from .serializers import marshal_json

from .metadata import ParamMetadata, find_field_metadata


def match_content_type(content_type: str, pattern: str) -> bool:
    if pattern in (content_type, "*", "*/*"):
        return True

    msg = Message()
    msg["content-type"] = content_type
    media_type = msg.get_content_type()

    if media_type == pattern:
        return True

    parts = media_type.split("/")
    if len(parts) == 2:
        if pattern in (f"{parts[0]}/*", f"*/{parts[1]}"):
            return True

    return False


def match_status_codes(status_codes: List[str], status_code: int) -> bool:
    if "default" in status_codes:
        return True

    for code in status_codes:
        if code == str(status_code):
            return True

        if code.endswith("XX") and code.startswith(str(status_code)[:1]):
            return True
    return False


T = TypeVar("T")


def get_global_from_env(
    value: Optional[T], env_key: str, type_cast: Callable[[str], T]
) -> Optional[T]:
    if value is not None:
        return value
    env_value = os.getenv(env_key)
    if env_value is not None:
        try:
            return type_cast(env_value)
        except ValueError:
            pass
    return None


def match_response(
    response: Response, code: Union[str, List[str]], content_type: str
) -> bool:
    codes = code if isinstance(code, list) else [code]
    return match_status_codes(codes, response.status_code) and match_content_type(
        response.headers.get("content-type", "application/octet-stream"), content_type
    )


def _populate_from_globals(
    param_name: str, value: Any, param_metadata_type: type, gbls: Any
) -> Tuple[Any, bool]:
    if gbls is None:
        return value, False

    if not isinstance(gbls, BaseModel):
        raise TypeError("globals must be a pydantic model")

    global_fields: Dict[str, FieldInfo] = gbls.__class__.model_fields
    found = False
    for name in global_fields:
        field = global_fields[name]
        if name is not param_name:
            continue

        found = True

        if value is not None:
            return value, True

        global_value = getattr(gbls, name)

        param_metadata = find_field_metadata(field, param_metadata_type)
        if param_metadata is None:
            return value, True

        return global_value, True

    return value, found


def _val_to_string(val) -> str:
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, datetime):
        return str(val.isoformat().replace("+00:00", "Z"))
    if isinstance(val, Enum):
        return str(val.value)

    return str(val)


def _get_serialized_params(
    metadata: ParamMetadata, field_name: str, obj: Any, typ: type
) -> Dict[str, str]:
    params: Dict[str, str] = {}

    serialization = metadata.serialization
    if serialization == "json":
        params[field_name] = marshal_json(obj, typ)

    return params


def _is_set(value: Any) -> bool:
    return value is not None and not isinstance(value, Unset)
