

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from typing import Optional
from typing_extensions import NotRequired, TypedDict


class GetUsersUsersResponseBodyData(BaseModel):
    message: Optional[str] = None
    r"""Error message indicating a server-side issue."""


class GetUsersUsersResponseBody(Exception):
    r"""Server error while retrieving users data."""

    data: GetUsersUsersResponseBodyData

    def __init__(self, data: GetUsersUsersResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, GetUsersUsersResponseBodyData)


class GetUsersUsersResponseResponseBodyData(BaseModel):
    message: Optional[str] = None
    r"""Error message indicating the missing configuration."""


class GetUsersUsersResponseResponseBody(Exception):
    r"""Missing user configuration."""

    data: GetUsersUsersResponseResponseBodyData

    def __init__(self, data: GetUsersUsersResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, GetUsersUsersResponseResponseBodyData)


class GetUsersResponseBodyTypedDict(TypedDict):
    user_id: NotRequired[int]
    r"""The unique identifier of the user."""
    full_name: NotRequired[str]
    r"""The full name of the user."""
    email: NotRequired[str]
    r"""The email address of the user."""
    status: NotRequired[bool]
    r"""The active status of the user account."""
    role: NotRequired[str]
    r"""The role assigned to the user."""
    department: NotRequired[str]
    r"""The department that the user belongs to."""


class GetUsersResponseBody(BaseModel):
    user_id: Optional[int] = None
    r"""The unique identifier of the user."""

    full_name: Optional[str] = None
    r"""The full name of the user."""

    email: Optional[str] = None
    r"""The email address of the user."""

    status: Optional[bool] = None
    r"""The active status of the user account."""

    role: Optional[str] = None
    r"""The role assigned to the user."""

    department: Optional[str] = None
    r"""The department that the user belongs to."""
