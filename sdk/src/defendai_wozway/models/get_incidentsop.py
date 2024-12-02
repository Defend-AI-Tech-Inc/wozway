

from __future__ import annotations
from datetime import datetime
from defendai_wozway.types import BaseModel
from defendai_wozway.utils import FieldMetadata, QueryParamMetadata
from enum import Enum
import pydantic
from typing import List, Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class QueryParamSortOrder(str, Enum):
    r"""Order of sorting."""

    ASC = "ASC"
    DESC = "DESC"


class GetIncidentsRequestTypedDict(TypedDict):
    duration: NotRequired[str]
    r"""Duration to filter incidents (e.g., day, week, month)."""
    page_size: NotRequired[int]
    r"""Number of records per page."""
    page_num: NotRequired[int]
    r"""Page number to retrieve."""
    sort_field: NotRequired[str]
    r"""Field to sort the records by."""
    sort_order: NotRequired[QueryParamSortOrder]
    r"""Order of sorting."""
    search: NotRequired[str]
    r"""Search term for filtering incident fields."""
    filters: NotRequired[str]
    r"""JSON string of filters, including severity and resolved status."""


class GetIncidentsRequest(BaseModel):
    duration: Annotated[
        Optional[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = "day"
    r"""Duration to filter incidents (e.g., day, week, month)."""

    page_size: Annotated[
        Optional[int],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = 10
    r"""Number of records per page."""

    page_num: Annotated[
        Optional[int],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = 1
    r"""Page number to retrieve."""

    sort_field: Annotated[
        Optional[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = "created_at"
    r"""Field to sort the records by."""

    sort_order: Annotated[
        Optional[QueryParamSortOrder],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = QueryParamSortOrder.DESC
    r"""Order of sorting."""

    search: Annotated[
        Optional[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""Search term for filtering incident fields."""

    filters: Annotated[
        Optional[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""JSON string of filters, including severity and resolved status."""


class GetIncidentsDataTypedDict(TypedDict):
    incident_id: NotRequired[int]
    r"""Unique ID of the incident"""
    policy_id: NotRequired[int]
    r"""ID of the policy associated with the incident"""
    policy_name: NotRequired[str]
    r"""Name of the policy"""
    incident_description: NotRequired[str]
    r"""Description of the incident"""
    severity: NotRequired[str]
    r"""Severity of the incident (e.g., LOW, MEDIUM, HIGH)"""
    similar_incidents_count: NotRequired[int]
    r"""Number of similar incidents"""
    context: NotRequired[str]
    r"""Context of the incident"""
    resolved: NotRequired[bool]
    r"""Whether the incident is resolved or not"""
    resolution_comments: NotRequired[str]
    r"""Comments related to the resolution of the incident"""
    created_at: NotRequired[datetime]
    r"""Date and time when the incident was created"""
    updated_time: NotRequired[datetime]
    r"""Date and time when the incident was last updated"""


class GetIncidentsData(BaseModel):
    incident_id: Optional[int] = None
    r"""Unique ID of the incident"""

    policy_id: Optional[int] = None
    r"""ID of the policy associated with the incident"""

    policy_name: Optional[str] = None
    r"""Name of the policy"""

    incident_description: Optional[str] = None
    r"""Description of the incident"""

    severity: Optional[str] = None
    r"""Severity of the incident (e.g., LOW, MEDIUM, HIGH)"""

    similar_incidents_count: Optional[int] = None
    r"""Number of similar incidents"""

    context: Optional[str] = None
    r"""Context of the incident"""

    resolved: Optional[bool] = None
    r"""Whether the incident is resolved or not"""

    resolution_comments: Optional[str] = None
    r"""Comments related to the resolution of the incident"""

    created_at: Optional[datetime] = None
    r"""Date and time when the incident was created"""

    updated_time: Optional[datetime] = None
    r"""Date and time when the incident was last updated"""


class GetIncidentsPaginationTypedDict(TypedDict):
    total_rows: NotRequired[int]
    r"""Total number of rows"""
    total_pages: NotRequired[int]
    r"""Total number of pages"""
    current_page: NotRequired[int]
    r"""Current page number"""
    page_size: NotRequired[int]
    r"""Number of records per page"""


class GetIncidentsPagination(BaseModel):
    total_rows: Annotated[Optional[int], pydantic.Field(alias="totalRows")] = None
    r"""Total number of rows"""

    total_pages: Annotated[Optional[int], pydantic.Field(alias="totalPages")] = None
    r"""Total number of pages"""

    current_page: Annotated[Optional[int], pydantic.Field(alias="currentPage")] = None
    r"""Current page number"""

    page_size: Annotated[Optional[int], pydantic.Field(alias="pageSize")] = None
    r"""Number of records per page"""


class GetIncidentsResponseBodyTypedDict(TypedDict):
    r"""List of incidents with pagination."""

    data: NotRequired[List[GetIncidentsDataTypedDict]]
    pagination: NotRequired[GetIncidentsPaginationTypedDict]


class GetIncidentsResponseBody(BaseModel):
    r"""List of incidents with pagination."""

    data: Optional[List[GetIncidentsData]] = None

    pagination: Optional[GetIncidentsPagination] = None
