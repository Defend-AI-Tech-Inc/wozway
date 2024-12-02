

from __future__ import annotations
from defendai_wozway.types import BaseModel
from defendai_wozway.utils import FieldMetadata, PathParamMetadata
from typing import Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class DeleteConnectionIDRequestTypedDict(TypedDict):
    id: str
    r"""ID of the connection to delete."""


class DeleteConnectionIDRequest(BaseModel):
    id: Annotated[
        str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))
    ]
    r"""ID of the connection to delete."""


class DeleteConnectionIDResponseBodyTypedDict(TypedDict):
    r"""Connection deleted successfully."""

    deleted_records: NotRequired[int]
    r"""Number of deleted records."""


class DeleteConnectionIDResponseBody(BaseModel):
    r"""Connection deleted successfully."""

    deleted_records: Optional[int] = None
    r"""Number of deleted records."""
