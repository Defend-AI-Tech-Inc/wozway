

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from typing import List, Optional
from typing_extensions import NotRequired, TypedDict


class GetConnectionsConnectionsResponseResponseBodyData(BaseModel):
    message: Optional[str] = None


class GetConnectionsConnectionsResponseResponseBody(Exception):
    r"""Error retrieving connections."""

    data: GetConnectionsConnectionsResponseResponseBodyData

    def __init__(self, data: GetConnectionsConnectionsResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, GetConnectionsConnectionsResponseResponseBodyData
        )


class GetConnectionsConnectionsResponseBodyData(BaseModel):
    message: Optional[str] = None


class GetConnectionsConnectionsResponseBody(Exception):
    r"""Missing user configuration."""

    data: GetConnectionsConnectionsResponseBodyData

    def __init__(self, data: GetConnectionsConnectionsResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, GetConnectionsConnectionsResponseBodyData)


class GetConnectionsResponsePayloadTypedDict(TypedDict):
    r"""Response payload details associated with the connection."""


class GetConnectionsResponsePayload(BaseModel):
    r"""Response payload details associated with the connection."""


class GetConnectionsDataTypedDict(TypedDict):
    id: NotRequired[str]
    r"""Connection ID."""
    connection_url: NotRequired[str]
    r"""URL of the connection."""
    api_key: NotRequired[str]
    r"""part of API key of the connection."""
    host: NotRequired[str]
    r"""Host address of the API."""
    name: NotRequired[str]
    r"""Name of the connection."""
    model_api_url: NotRequired[str]
    r"""URL of the model API."""
    model_name_list: NotRequired[List[str]]
    r"""List of model names available in the connection."""
    response_payload: NotRequired[GetConnectionsResponsePayloadTypedDict]
    r"""Response payload details associated with the connection."""


class GetConnectionsData(BaseModel):
    id: Optional[str] = None
    r"""Connection ID."""

    connection_url: Optional[str] = None
    r"""URL of the connection."""

    api_key: Optional[str] = None
    r"""part of API key of the connection."""

    host: Optional[str] = None
    r"""Host address of the API."""

    name: Optional[str] = None
    r"""Name of the connection."""

    model_api_url: Optional[str] = None
    r"""URL of the model API."""

    model_name_list: Optional[List[str]] = None
    r"""List of model names available in the connection."""

    response_payload: Optional[GetConnectionsResponsePayload] = None
    r"""Response payload details associated with the connection."""


class GetConnectionsResponseBodyTypedDict(TypedDict):
    r"""Successfully retrieved all connections."""

    data: NotRequired[List[GetConnectionsDataTypedDict]]


class GetConnectionsResponseBody(BaseModel):
    r"""Successfully retrieved all connections."""

    data: Optional[List[GetConnectionsData]] = None
