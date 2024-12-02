

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from typing import Optional
from typing_extensions import NotRequired, TypedDict


class GetApplicationsApplicationsResponseBodyData(BaseModel):
    message: Optional[str] = None


class GetApplicationsApplicationsResponseBody(Exception):
    r"""Server error while retrieving applications data."""

    data: GetApplicationsApplicationsResponseBodyData

    def __init__(self, data: GetApplicationsApplicationsResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, GetApplicationsApplicationsResponseBodyData
        )


class GetApplicationsResponseBodyData(BaseModel):
    message: Optional[str] = None


class GetApplicationsResponseBody(Exception):
    r"""Missing user configuration."""

    data: GetApplicationsResponseBodyData

    def __init__(self, data: GetApplicationsResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(self.data, GetApplicationsResponseBodyData)


class ResponseBodyTypedDict(TypedDict):
    app_id: NotRequired[int]
    r"""Unique identifier of the application."""
    name: NotRequired[str]
    r"""Name of the application."""
    description: NotRequired[str]
    r"""Description of the application."""
    connection_id: NotRequired[int]
    r"""ID of the connection associated with the application."""
    connection_name: NotRequired[str]
    r"""Name of the associated connection."""
    status: NotRequired[bool]
    r"""Indicates if the application is active."""
    total_api_keys: NotRequired[int]
    r"""Total number of API keys associated with the application."""


class ResponseBody(BaseModel):
    app_id: Optional[int] = None
    r"""Unique identifier of the application."""

    name: Optional[str] = None
    r"""Name of the application."""

    description: Optional[str] = None
    r"""Description of the application."""

    connection_id: Optional[int] = None
    r"""ID of the connection associated with the application."""

    connection_name: Optional[str] = None
    r"""Name of the associated connection."""

    status: Optional[bool] = None
    r"""Indicates if the application is active."""

    total_api_keys: Optional[int] = None
    r"""Total number of API keys associated with the application."""
