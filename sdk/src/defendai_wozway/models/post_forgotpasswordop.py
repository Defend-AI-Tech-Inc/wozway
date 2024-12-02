

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
import pydantic
from typing import Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class PostForgotPasswordRequestBodyTypedDict(TypedDict):
    email: NotRequired[str]
    r"""The email address of the user requesting password reset."""
    tenant_id: NotRequired[str]
    r"""The ID of the tenant to which the user belongs."""


class PostForgotPasswordRequestBody(BaseModel):
    email: Optional[str] = None
    r"""The email address of the user requesting password reset."""

    tenant_id: Annotated[Optional[str], pydantic.Field(alias="tenantId")] = None
    r"""The ID of the tenant to which the user belongs."""


class PostForgotPasswordUsersResponseResponseBodyData(BaseModel):
    error: Optional[str] = None
    r"""Error message indicating server-side failure in sending the email or updating the user."""


class PostForgotPasswordUsersResponseResponseBody(Exception):
    r"""Internal server error."""

    data: PostForgotPasswordUsersResponseResponseBodyData

    def __init__(self, data: PostForgotPasswordUsersResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, PostForgotPasswordUsersResponseResponseBodyData
        )


class PostForgotPasswordUsersResponseBodyData(BaseModel):
    error: Optional[str] = None
    r"""Error message indicating an invalid tenant ID or email not registered."""


class PostForgotPasswordUsersResponseBody(Exception):
    r"""Tenant ID or email not found."""

    data: PostForgotPasswordUsersResponseBodyData

    def __init__(self, data: PostForgotPasswordUsersResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, PostForgotPasswordUsersResponseBodyData)


class PostForgotPasswordResponseBodyTypedDict(TypedDict):
    r"""Password reset email sent successfully."""

    success: NotRequired[str]
    r"""Success message confirming the email has been sent."""


class PostForgotPasswordResponseBody(BaseModel):
    r"""Password reset email sent successfully."""

    success: Optional[str] = None
    r"""Success message confirming the email has been sent."""
