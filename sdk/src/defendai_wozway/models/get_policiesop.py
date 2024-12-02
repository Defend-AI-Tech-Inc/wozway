

from __future__ import annotations
from datetime import datetime
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from defendai_wozway.utils import FieldMetadata, QueryParamMetadata
from enum import Enum
import pydantic
from typing import List, Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class GetPoliciesQueryParamSortOrder(str, Enum):
    r"""The order of sorting (ascending or descending)."""

    ASC = "ASC"
    DESC = "DESC"


class GetPoliciesRequestTypedDict(TypedDict):
    page_size: NotRequired[int]
    r"""The number of policies per page."""
    page_num: NotRequired[int]
    r"""The current page number."""
    sort_field: NotRequired[str]
    r"""Field by which to sort the policies."""
    sort_order: NotRequired[GetPoliciesQueryParamSortOrder]
    r"""The order of sorting (ascending or descending)."""
    search: NotRequired[str]
    r"""Search term to filter policies by name or description (minimum 3 characters)."""
    filters: NotRequired[str]
    r"""JSON string of additional filters, including \"policyType\", \"direction\", and \"policyAction\"."""


class GetPoliciesRequest(BaseModel):
    page_size: Annotated[
        Optional[int],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = 10
    r"""The number of policies per page."""

    page_num: Annotated[
        Optional[int],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = 1
    r"""The current page number."""

    sort_field: Annotated[
        Optional[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = "policy_name"
    r"""Field by which to sort the policies."""

    sort_order: Annotated[
        Optional[GetPoliciesQueryParamSortOrder],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = GetPoliciesQueryParamSortOrder.DESC
    r"""The order of sorting (ascending or descending)."""

    search: Annotated[
        Optional[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""Search term to filter policies by name or description (minimum 3 characters)."""

    filters: Annotated[
        Optional[str],
        FieldMetadata(query=QueryParamMetadata(style="form", explode=True)),
    ] = None
    r"""JSON string of additional filters, including \"policyType\", \"direction\", and \"policyAction\"."""


class GetPoliciesPoliciesResponseResponseBodyData(BaseModel):
    message: Optional[str] = None


class GetPoliciesPoliciesResponseResponseBody(Exception):
    r"""Internal server error."""

    data: GetPoliciesPoliciesResponseResponseBodyData

    def __init__(self, data: GetPoliciesPoliciesResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, GetPoliciesPoliciesResponseResponseBodyData
        )


class GetPoliciesPoliciesResponseBodyData(BaseModel):
    message: Optional[str] = None


class GetPoliciesPoliciesResponseBody(Exception):
    r"""Bad request, possibly due to missing or invalid query parameters."""

    data: GetPoliciesPoliciesResponseBodyData

    def __init__(self, data: GetPoliciesPoliciesResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, GetPoliciesPoliciesResponseBodyData)


class GetPoliciesAttributesTypedDict(TypedDict):
    policies_type_attribute_id: NotRequired[int]
    attribute_name: NotRequired[str]
    attribute_value: NotRequired[str]


class GetPoliciesAttributes(BaseModel):
    policies_type_attribute_id: Optional[int] = None

    attribute_name: Optional[str] = None

    attribute_value: Optional[str] = None


class GetPoliciesPolicyTypesTypedDict(TypedDict):
    policy_type_id: NotRequired[int]
    policy_type: NotRequired[str]
    policy_type_value: NotRequired[str]
    attributes: NotRequired[List[GetPoliciesAttributesTypedDict]]


class GetPoliciesPolicyTypes(BaseModel):
    policy_type_id: Optional[int] = None

    policy_type: Optional[str] = None

    policy_type_value: Optional[str] = None

    attributes: Optional[List[GetPoliciesAttributes]] = None


class GetPoliciesDataTypedDict(TypedDict):
    policy_id: NotRequired[int]
    policy_name: NotRequired[str]
    policy_description: NotRequired[str]
    direction: NotRequired[str]
    policy_action: NotRequired[str]
    app_id_list: NotRequired[List[str]]
    is_default: NotRequired[bool]
    status: NotRequired[bool]
    updated_time: NotRequired[datetime]
    policy_types: NotRequired[List[GetPoliciesPolicyTypesTypedDict]]


class GetPoliciesData(BaseModel):
    policy_id: Optional[int] = None

    policy_name: Optional[str] = None

    policy_description: Optional[str] = None

    direction: Optional[str] = None

    policy_action: Optional[str] = None

    app_id_list: Optional[List[str]] = None

    is_default: Optional[bool] = None

    status: Optional[bool] = None

    updated_time: Optional[datetime] = None

    policy_types: Optional[List[GetPoliciesPolicyTypes]] = None


class GetPoliciesPaginationTypedDict(TypedDict):
    total_rows: NotRequired[int]
    total_pages: NotRequired[int]
    current_page: NotRequired[int]
    page_size: NotRequired[int]


class GetPoliciesPagination(BaseModel):
    total_rows: Annotated[Optional[int], pydantic.Field(alias="totalRows")] = None

    total_pages: Annotated[Optional[int], pydantic.Field(alias="totalPages")] = None

    current_page: Annotated[Optional[int], pydantic.Field(alias="currentPage")] = None

    page_size: Annotated[Optional[int], pydantic.Field(alias="pageSize")] = None


class GetPoliciesResponseBodyTypedDict(TypedDict):
    r"""A paginated list of policies."""

    data: NotRequired[List[GetPoliciesDataTypedDict]]
    pagination: NotRequired[GetPoliciesPaginationTypedDict]


class GetPoliciesResponseBody(BaseModel):
    r"""A paginated list of policies."""

    data: Optional[List[GetPoliciesData]] = None

    pagination: Optional[GetPoliciesPagination] = None
