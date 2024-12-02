

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from defendai_wozway.utils import FieldMetadata, QueryParamMetadata
from typing import Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class DeleteApplicationRequestTypedDict(TypedDict):
    app_id: int
    r"""The ID of the application to delete."""


class DeleteApplicationRequest(BaseModel):
    app_id: Annotated[
        int, FieldMetadata(query=QueryParamMetadata(style="form", explode=True))
    ]
    r"""The ID of the application to delete."""


class DeleteApplicationApplicationsResponseResponseBodyData(BaseModel):
    message: Optional[str] = None


class DeleteApplicationApplicationsResponseResponseBody(Exception):
    r"""Server error while deleting the application."""

    data: DeleteApplicationApplicationsResponseResponseBodyData

    def __init__(self, data: DeleteApplicationApplicationsResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, DeleteApplicationApplicationsResponseResponseBodyData
        )


class DeleteApplicationApplicationsResponseBodyData(BaseModel):
    message: Optional[str] = None


class DeleteApplicationApplicationsResponseBody(Exception):
    r"""Missing user configuration or app_id."""

    data: DeleteApplicationApplicationsResponseBodyData

    def __init__(self, data: DeleteApplicationApplicationsResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, DeleteApplicationApplicationsResponseBodyData
        )


class DeleteApplicationResponseBodyTypedDict(TypedDict):
    r"""Application deleted successfully."""

    deleted_records: NotRequired[int]
    r"""The number of records deleted."""


class DeleteApplicationResponseBody(BaseModel):
    r"""Application deleted successfully."""

    deleted_records: Optional[int] = None
    r"""The number of records deleted."""
