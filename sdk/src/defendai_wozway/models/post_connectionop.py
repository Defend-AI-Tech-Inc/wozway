

from __future__ import annotations
from defendai_wozway.types import BaseModel
from typing import List, Optional
from typing_extensions import NotRequired, TypedDict


class ResponsePayloadTypedDict(TypedDict):
    r"""Response payload details associated with the connection."""


class ResponsePayload(BaseModel):
    r"""Response payload details associated with the connection."""


class PostConnectionRequestBodyTypedDict(TypedDict):
    id: NotRequired[str]
    r"""ID of the connection. Omit this field when creating a new connection"""
    connection_url: NotRequired[str]
    r"""The URL of the connection."""
    api_key: NotRequired[str]
    r"""API key for the connection."""
    host: NotRequired[str]
    r"""Host address of the API."""
    name: NotRequired[str]
    r"""Name of the connection."""
    model_api_url: NotRequired[str]
    r"""URL of the model API."""
    model_name_list: NotRequired[List[str]]
    r"""List of model names available in the connection."""
    response_payload: NotRequired[ResponsePayloadTypedDict]
    r"""Response payload details associated with the connection."""


class PostConnectionRequestBody(BaseModel):
    id: Optional[str] = None
    r"""ID of the connection. Omit this field when creating a new connection"""

    connection_url: Optional[str] = None
    r"""The URL of the connection."""

    api_key: Optional[str] = None
    r"""API key for the connection."""

    host: Optional[str] = None
    r"""Host address of the API."""

    name: Optional[str] = None
    r"""Name of the connection."""

    model_api_url: Optional[str] = None
    r"""URL of the model API."""

    model_name_list: Optional[List[str]] = None
    r"""List of model names available in the connection."""

    response_payload: Optional[ResponsePayload] = None
    r"""Response payload details associated with the connection."""


class PostConnectionDataTypedDict(TypedDict):
    r"""Details of the saved connection."""


class PostConnectionData(BaseModel):
    r"""Details of the saved connection."""


class PostConnectionResponseBodyTypedDict(TypedDict):
    r"""Successfully saved or updated the connection."""

    data: NotRequired[PostConnectionDataTypedDict]
    r"""Details of the saved connection."""


class PostConnectionResponseBody(BaseModel):
    r"""Successfully saved or updated the connection."""

    data: Optional[PostConnectionData] = None
    r"""Details of the saved connection."""
