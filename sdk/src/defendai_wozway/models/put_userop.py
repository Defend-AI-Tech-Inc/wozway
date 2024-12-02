

from __future__ import annotations
from defendai_wozway.types import BaseModel
import pydantic
from typing import Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class PutUserRequestBodyTypedDict(TypedDict):
    user_id: NotRequired[str]
    r"""The user's ID."""
    full_name: NotRequired[str]
    r"""The user's full name."""
    email: NotRequired[str]
    r"""The user's email."""
    timezone: NotRequired[str]
    r"""The user's timezone."""
    role: NotRequired[str]
    r"""The user's role."""
    department: NotRequired[str]
    r"""The department that the user belongs to."""


class PutUserRequestBody(BaseModel):
    user_id: Optional[str] = None
    r"""The user's ID."""

    full_name: Optional[str] = None
    r"""The user's full name."""

    email: Optional[str] = None
    r"""The user's email."""

    timezone: Optional[str] = None
    r"""The user's timezone."""

    role: Optional[str] = None
    r"""The user's role."""

    department: Optional[str] = None
    r"""The department that the user belongs to."""


class PutUserResponseBodyTypedDict(TypedDict):
    r"""Successfully updated user."""

    updated_id: NotRequired[str]
    r"""The ID of the updated user."""


class PutUserResponseBody(BaseModel):
    r"""Successfully updated user."""

    updated_id: Annotated[Optional[str], pydantic.Field(alias="updatedId")] = None
    r"""The ID of the updated user."""
