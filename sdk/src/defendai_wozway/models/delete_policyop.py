

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from defendai_wozway.utils import FieldMetadata, QueryParamMetadata
from typing import Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class DeletePolicyRequestTypedDict(TypedDict):
    policy_id: int
    r"""The ID of the policy to delete."""


class DeletePolicyRequest(BaseModel):
    policy_id: Annotated[
        int, FieldMetadata(query=QueryParamMetadata(style="form", explode=True))
    ]
    r"""The ID of the policy to delete."""


class DeletePolicyPoliciesResponseResponseBodyData(BaseModel):
    message: Optional[str] = None


class DeletePolicyPoliciesResponseResponseBody(Exception):
    r"""Server error while deleting the policy."""

    data: DeletePolicyPoliciesResponseResponseBodyData

    def __init__(self, data: DeletePolicyPoliciesResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, DeletePolicyPoliciesResponseResponseBodyData
        )


class DeletePolicyPoliciesResponseBodyData(BaseModel):
    message: Optional[str] = None


class DeletePolicyPoliciesResponseBody(Exception):
    r"""Missing configuration or invalid policy ID."""

    data: DeletePolicyPoliciesResponseBodyData

    def __init__(self, data: DeletePolicyPoliciesResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, DeletePolicyPoliciesResponseBodyData)


class DeletePolicyResponseBodyTypedDict(TypedDict):
    r"""Policy deleted successfully."""

    deleted_records: NotRequired[int]


class DeletePolicyResponseBody(BaseModel):
    r"""Policy deleted successfully."""

    deleted_records: Optional[int] = None
