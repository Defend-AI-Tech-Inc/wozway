

from __future__ import annotations
from defendai_wozway.types import BaseModel
from defendai_wozway.utils import FieldMetadata, QueryParamMetadata
from typing import Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class DeleteUserRequestTypedDict(TypedDict):
    user_id: str
    r"""The ID of the user to delete."""


class DeleteUserRequest(BaseModel):
    user_id: Annotated[
        str, FieldMetadata(query=QueryParamMetadata(style="form", explode=True))
    ]
    r"""The ID of the user to delete."""


class DeleteUserResponseBodyTypedDict(TypedDict):
    r"""Successfully deleted user."""

    deleted_records: NotRequired[int]
    r"""The number of deleted records."""


class DeleteUserResponseBody(BaseModel):
    r"""Successfully deleted user."""

    deleted_records: Optional[int] = None
    r"""The number of deleted records."""
