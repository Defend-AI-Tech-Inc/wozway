

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from typing import List, Optional
from typing_extensions import NotRequired, TypedDict


class AttributesTypedDict(TypedDict):
    attribute_name: NotRequired[str]
    r"""Name of the attribute."""
    attribute_value: NotRequired[str]
    r"""Value of the attribute."""


class Attributes(BaseModel):
    attribute_name: Optional[str] = None
    r"""Name of the attribute."""

    attribute_value: Optional[str] = None
    r"""Value of the attribute."""


class PolicyTypesTypedDict(TypedDict):
    policy_type: NotRequired[str]
    r"""Type of policy( e.g., Regex, Privacy, Code, Similarity, Phishing URL, Ban topics)."""
    policy_type_value: NotRequired[str]
    r"""Specific value related to policy type."""
    attributes: NotRequired[List[AttributesTypedDict]]


class PolicyTypes(BaseModel):
    policy_type: Optional[str] = None
    r"""Type of policy( e.g., Regex, Privacy, Code, Similarity, Phishing URL, Ban topics)."""

    policy_type_value: Optional[str] = None
    r"""Specific value related to policy type."""

    attributes: Optional[List[Attributes]] = None


class PostPolicyRequestBodyTypedDict(TypedDict):
    policy_name: NotRequired[str]
    r"""The name of the policy."""
    policy_description: NotRequired[str]
    r"""Detailed description of the policy."""
    direction: NotRequired[str]
    r"""Direction of policy enforcement (e.g., PROMPT, RESPONSE)."""
    policy_action: NotRequired[str]
    r"""Action to take when the policy is triggered(ALLOW,  BLOCK, ALERT)."""
    app_id: NotRequired[List[str]]
    r"""List of application IDs the policy applies to."""
    policy_types: NotRequired[List[PolicyTypesTypedDict]]
    r"""List of policy types, each with attributes."""


class PostPolicyRequestBody(BaseModel):
    policy_name: Optional[str] = None
    r"""The name of the policy."""

    policy_description: Optional[str] = None
    r"""Detailed description of the policy."""

    direction: Optional[str] = None
    r"""Direction of policy enforcement (e.g., PROMPT, RESPONSE)."""

    policy_action: Optional[str] = None
    r"""Action to take when the policy is triggered(ALLOW,  BLOCK, ALERT)."""

    app_id: Optional[List[str]] = None
    r"""List of application IDs the policy applies to."""

    policy_types: Optional[List[PolicyTypes]] = None
    r"""List of policy types, each with attributes."""


class PostPolicyPoliciesResponseResponseBodyData(BaseModel):
    message: Optional[str] = None


class PostPolicyPoliciesResponseResponseBody(Exception):
    r"""Server error while creating the policy."""

    data: PostPolicyPoliciesResponseResponseBodyData

    def __init__(self, data: PostPolicyPoliciesResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, PostPolicyPoliciesResponseResponseBodyData)


class PostPolicyPoliciesResponseBodyData(BaseModel):
    message: Optional[str] = None


class PostPolicyPoliciesResponseBody(Exception):
    r"""Missing user configuration."""

    data: PostPolicyPoliciesResponseBodyData

    def __init__(self, data: PostPolicyPoliciesResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, PostPolicyPoliciesResponseBodyData)


class PostPolicyResponseBodyTypedDict(TypedDict):
    r"""Policy created successfully."""

    message: NotRequired[str]


class PostPolicyResponseBody(BaseModel):
    r"""Policy created successfully."""

    message: Optional[str] = None
