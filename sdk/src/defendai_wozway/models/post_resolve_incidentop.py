

from __future__ import annotations
from defendai_wozway.types import BaseModel
from typing import Optional
from typing_extensions import NotRequired, TypedDict


class PostResolveIncidentRequestBodyTypedDict(TypedDict):
    incident_id: NotRequired[int]
    r"""Unique identifier of the incident."""
    comments: NotRequired[str]
    r"""Comments regarding the resolution."""


class PostResolveIncidentRequestBody(BaseModel):
    incident_id: Optional[int] = None
    r"""Unique identifier of the incident."""

    comments: Optional[str] = None
    r"""Comments regarding the resolution."""


class PostResolveIncidentResponseBodyTypedDict(TypedDict):
    r"""Incident resolved successfully."""

    updated_records: NotRequired[int]
    r"""Number of records updated."""


class PostResolveIncidentResponseBody(BaseModel):
    r"""Incident resolved successfully."""

    updated_records: Optional[int] = None
    r"""Number of records updated."""
