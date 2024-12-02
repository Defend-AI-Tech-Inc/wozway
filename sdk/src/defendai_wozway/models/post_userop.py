

from __future__ import annotations
from defendai_wozway.types import BaseModel
import pydantic
from typing import Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class PostUserRequestBodyTypedDict(TypedDict):
    full_name: NotRequired[str]
    r"""The user's full name."""
    email: NotRequired[str]
    r"""The user's email address."""
    timezone: NotRequired[str]
    r"""The user's timezone."""
    role: NotRequired[str]
    r"""The user's role."""
    department: NotRequired[str]
    r"""The department that the user belongs to."""


class PostUserRequestBody(BaseModel):
    full_name: Optional[str] = None
    r"""The user's full name."""

    email: Optional[str] = None
    r"""The user's email address."""

    timezone: Optional[str] = None
    r"""The user's timezone."""

    role: Optional[str] = None
    r"""The user's role."""

    department: Optional[str] = None
    r"""The department that the user belongs to."""


class PostUserResponseBodyTypedDict(TypedDict):
    r"""Successfully saved user."""

    saved_id: NotRequired[str]
    r"""The ID of the saved user."""


class PostUserResponseBody(BaseModel):
    r"""Successfully saved user."""

    saved_id: Annotated[Optional[str], pydantic.Field(alias="savedId")] = None
    r"""The ID of the saved user."""
