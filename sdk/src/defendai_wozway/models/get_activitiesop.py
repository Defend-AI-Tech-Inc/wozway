

from __future__ import annotations
from datetime import datetime
from defendai_wozway.types import BaseModel
from defendai_wozway.utils import FieldMetadata, QueryParamMetadata
from enum import Enum
import pydantic
from typing import List, Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class Duration(str, Enum):
    r"""Time range to filter activities (e.g., 'day' for last 24 hours)."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class SortField(str, Enum):
    r"""Field by which to sort results."""

    CREATED_AT = "created_at"
    MODEL_NAME = "model_name"
    VERDICT = "verdict"


class SortOrder(str, Enum):
    r"""Sort order (ascending or descending)."""

    ASC = "ASC"
    DESC = "DESC"


class GetActivitiesRequestTypedDict(TypedDict):
    duration: NotRequired[Duration]
    r"""Time range to filter activities (e.g., 'day' for last 24 hours)."""
    page_size: NotRequired[int]
    r"""Number of records per page."""
    page_num: NotRequired[int]
    r"""Page number to retrieve."""
    sort_field: NotRequired[SortField]
    r"""Field by which to sort results."""
    sort_order: NotRequired[SortOrder]
    r"""Sort order (ascending or descending)."""
    search: NotRequired[str]
    r"""Search term to filter by input, output, context, or verdict fields."""
    filters: NotRequired[str]
    r"""JSON string to filter activities by verdict (ALLOW, ALERT, BLOCK), application names, and model names."""


class GetActivitiesRequest(BaseModel):
    duration: Annotated[
        Optional[Duration],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""Time range to filter activities (e.g., 'day' for last 24 hours)."""

    page_size: Annotated[
        Optional[int],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""Number of records per page."""

    page_num: Annotated[
        Optional[int],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""Page number to retrieve."""

    sort_field: Annotated[
        Optional[SortField],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""Field by which to sort results."""

    sort_order: Annotated[
        Optional[SortOrder],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""Sort order (ascending or descending)."""

    search: Annotated[
        Optional[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""Search term to filter by input, output, context, or verdict fields."""

    filters: Annotated[
        Optional[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""JSON string to filter activities by verdict (ALLOW, ALERT, BLOCK), application names, and model names."""


class DataTypedDict(TypedDict):
    model_name: NotRequired[str]
    input: NotRequired[str]
    context: NotRequired[str]
    output: NotRequired[str]
    verdict: NotRequired[str]
    entity_id: NotRequired[int]
    created_at: NotRequired[datetime]
    activity_time: NotRequired[str]
    r"""Timestamp in the specified timezone."""
    app_id: NotRequired[int]
    name: NotRequired[str]
    r"""Application name."""
    api_key: NotRequired[str]
    r"""API key of the application."""
    user_name: NotRequired[str]
    r"""The name of the user associated with the activity."""


class Data(BaseModel):
    model_name: Optional[str] = None

    input: Optional[str] = None

    context: Optional[str] = None

    output: Optional[str] = None

    verdict: Optional[str] = None

    entity_id: Optional[int] = None

    created_at: Optional[datetime] = None

    activity_time: Optional[str] = None
    r"""Timestamp in the specified timezone."""

    app_id: Optional[int] = None

    name: Optional[str] = None
    r"""Application name."""

    api_key: Optional[str] = None
    r"""API key of the application."""

    user_name: Optional[str] = None
    r"""The name of the user associated with the activity."""


class PaginationTypedDict(TypedDict):
    total_rows: NotRequired[int]
    total_pages: NotRequired[int]
    current_page: NotRequired[int]
    page_size: NotRequired[int]


class Pagination(BaseModel):
    total_rows: Annotated[Optional[int], pydantic.Field(alias="totalRows")] = None

    total_pages: Annotated[Optional[int], pydantic.Field(alias="totalPages")] = None

    current_page: Annotated[Optional[int], pydantic.Field(alias="currentPage")] = None

    page_size: Annotated[Optional[int], pydantic.Field(alias="pageSize")] = None


class GetActivitiesResponseBodyTypedDict(TypedDict):
    r"""Successful retrieval of activities data."""

    data: NotRequired[List[DataTypedDict]]
    pagination: NotRequired[PaginationTypedDict]


class GetActivitiesResponseBody(BaseModel):
    r"""Successful retrieval of activities data."""

    data: Optional[List[Data]] = None

    pagination: Optional[Pagination] = None
