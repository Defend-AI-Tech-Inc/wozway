

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from defendai_wozway.utils import FieldMetadata, QueryParamMetadata
from typing import Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class DeleteAPIKeyRequestTypedDict(TypedDict):
    api_key: str
    r"""The API key to delete."""


class DeleteAPIKeyRequest(BaseModel):
    api_key: Annotated[
        str, FieldMetadata(query=QueryParamMetadata(style="form", explode=True))
    ]
    r"""The API key to delete."""


class DeleteAPIKeyAPIKeysResponseResponseBodyData(BaseModel):
    message: Optional[str] = None


class DeleteAPIKeyAPIKeysResponseResponseBody(Exception):
    r"""Server error while deleting the API key."""

    data: DeleteAPIKeyAPIKeysResponseResponseBodyData

    def __init__(self, data: DeleteAPIKeyAPIKeysResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, DeleteAPIKeyAPIKeysResponseResponseBodyData
        )


class DeleteAPIKeyAPIKeysResponseBodyData(BaseModel):
    message: Optional[str] = None


class DeleteAPIKeyAPIKeysResponseBody(Exception):
    r"""Missing or invalid API key format, or missing user configuration."""

    data: DeleteAPIKeyAPIKeysResponseBodyData

    def __init__(self, data: DeleteAPIKeyAPIKeysResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, DeleteAPIKeyAPIKeysResponseBodyData)


class DeleteAPIKeyResponseBodyTypedDict(TypedDict):
    r"""API key deleted successfully."""

    deleted_records: NotRequired[int]
    r"""The number of records deleted."""


class DeleteAPIKeyResponseBody(BaseModel):
    r"""API key deleted successfully."""

    deleted_records: Optional[int] = None
    r"""The number of records deleted."""
