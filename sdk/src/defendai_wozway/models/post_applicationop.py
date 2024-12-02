

from __future__ import annotations
from defendai_wozway import utils
from defendai_wozway.types import BaseModel
from typing import Optional, Union
from typing_extensions import NotRequired, TypeAliasType, TypedDict


class PostApplicationRequestBodyTypedDict(TypedDict):
    app_id: NotRequired[int]
    r"""ID of the application to update (optional)."""
    name: NotRequired[str]
    r"""Name of the application."""
    description: NotRequired[str]
    r"""Description of the application."""
    connection_id: NotRequired[int]
    r"""ID of the associated connection ( OpenAI, Groq etc)."""


class PostApplicationRequestBody(BaseModel):
    app_id: Optional[int] = None
    r"""ID of the application to update (optional)."""

    name: Optional[str] = None
    r"""Name of the application."""

    description: Optional[str] = None
    r"""Description of the application."""

    connection_id: Optional[int] = None
    r"""ID of the associated connection ( OpenAI, Groq etc)."""


class PostApplicationApplicationsResponse500ResponseBodyData(BaseModel):
    message: Optional[str] = None


class PostApplicationApplicationsResponse500ResponseBody(Exception):
    r"""Server error while creating or updating application."""

    data: PostApplicationApplicationsResponse500ResponseBodyData

    def __init__(self, data: PostApplicationApplicationsResponse500ResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, PostApplicationApplicationsResponse500ResponseBodyData
        )


class PostApplicationApplicationsResponse404ResponseBodyData(BaseModel):
    message: Optional[str] = None


class PostApplicationApplicationsResponse404ResponseBody(Exception):
    r"""Application not found."""

    data: PostApplicationApplicationsResponse404ResponseBodyData

    def __init__(self, data: PostApplicationApplicationsResponse404ResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, PostApplicationApplicationsResponse404ResponseBodyData
        )


class PostApplicationApplicationsResponseResponseBodyData(BaseModel):
    message: Optional[str] = None


class PostApplicationApplicationsResponseResponseBody(Exception):
    r"""Missing user configuration."""

    data: PostApplicationApplicationsResponseResponseBodyData

    def __init__(self, data: PostApplicationApplicationsResponseResponseBodyData):
        self.data = data

    def __str__(self) -> str:
        return utils.marshal_json(
            self.data, PostApplicationApplicationsResponseResponseBodyData
        )


class PostApplicationApplicationsResponseBodyTypedDict(TypedDict):
    r"""Application created successfully."""

    message: NotRequired[str]


class PostApplicationApplicationsResponseBody(BaseModel):
    r"""Application created successfully."""

    message: Optional[str] = None


class PostApplicationResponseBodyTypedDict(TypedDict):
    r"""Application updated successfully."""

    message: NotRequired[str]


class PostApplicationResponseBody(BaseModel):
    r"""Application updated successfully."""

    message: Optional[str] = None


PostApplicationResponseTypedDict = TypeAliasType(
    "PostApplicationResponseTypedDict",
    Union[
        PostApplicationResponseBodyTypedDict,
        PostApplicationApplicationsResponseBodyTypedDict,
    ],
)


PostApplicationResponse = TypeAliasType(
    "PostApplicationResponse",
    Union[PostApplicationResponseBody, PostApplicationApplicationsResponseBody],
)
