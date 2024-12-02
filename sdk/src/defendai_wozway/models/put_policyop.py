

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from typing import List, Optional
from typing_extensions import NotRequired, TypedDict


class PutPolicyAttributesTypedDict(TypedDict):
    attribute_name: NotRequired[str]
    r"""Name of the attribute."""
    attribute_value: NotRequired[str]
    r"""Value of the attribute."""


class PutPolicyAttributes(BaseModel):
    attribute_name: Optional[str] = None
    r"""Name of the attribute."""

    attribute_value: Optional[str] = None
    r"""Value of the attribute."""


class PutPolicyPolicyTypesTypedDict(TypedDict):
    policy_type: NotRequired[str]
    r"""Type of policy."""
    policy_type_value: NotRequired[str]
    r"""Specific value related to policy type."""
    attributes: NotRequired[List[PutPolicyAttributesTypedDict]]


class PutPolicyPolicyTypes(BaseModel):
    policy_type: Optional[str] = None
    r"""Type of policy."""

    policy_type_value: Optional[str] = None
    r"""Specific value related to policy type."""

    attributes: Optional[List[PutPolicyAttributes]] = None


class PutPolicyRequestBodyTypedDict(TypedDict):
    policy_id: NotRequired[int]
    r"""The ID of the policy to update."""
    policy_name: NotRequired[str]
    r"""The name of the policy."""
    policy_description: NotRequired[str]
    r"""Detailed description of the policy."""
    direction: NotRequired[str]
    r"""Direction of policy enforcement (e.g., PROMPT, RESPONSE)."""
    policy_action: NotRequired[str]
    r"""Action to take when the policy is triggered(ALLOW, BLOCK, ALERT)."""
    app_id: NotRequired[List[str]]
    r"""List of application IDs the policy applies to."""
    policy_types: NotRequired[List[PutPolicyPolicyTypesTypedDict]]
    r"""List of policy types, each with attributes."""


class PutPolicyRequestBody(BaseModel):
    policy_id: Optional[int] = None
    r"""The ID of the policy to update."""

    policy_name: Optional[str] = None
    r"""The name of the policy."""

    policy_description: Optional[str] = None
    r"""Detailed description of the policy."""

    direction: Optional[str] = None
    r"""Direction of policy enforcement (e.g., PROMPT, RESPONSE)."""

    policy_action: Optional[str] = None
    r"""Action to take when the policy is triggered(ALLOW, BLOCK, ALERT)."""

    app_id: Optional[List[str]] = None
    r"""List of application IDs the policy applies to."""

    policy_types: Optional[List[PutPolicyPolicyTypes]] = None
    r"""List of policy types, each with attributes."""


class PutPolicyPoliciesResponseResponseBodyData(BaseModel):
    message: Optional[str] = None


class PutPolicyPoliciesResponseResponseBody(Exception):
    r"""Server error while updating the policy."""

    data: PutPolicyPoliciesResponseResponseBodyData

    def __init__(self, data: PutPolicyPoliciesResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, PutPolicyPoliciesResponseResponseBodyData)


class PutPolicyPoliciesResponseBodyData(BaseModel):
    message: Optional[str] = None


class PutPolicyPoliciesResponseBody(Exception):
    r"""Missing configuration or invalid policy ID."""

    data: PutPolicyPoliciesResponseBodyData

    def __init__(self, data: PutPolicyPoliciesResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, PutPolicyPoliciesResponseBodyData)


class PutPolicyResponseBodyTypedDict(TypedDict):
    r"""Policy updated successfully."""

    message: NotRequired[str]


class PutPolicyResponseBody(BaseModel):
    r"""Policy updated successfully."""

    message: Optional[str] = None
