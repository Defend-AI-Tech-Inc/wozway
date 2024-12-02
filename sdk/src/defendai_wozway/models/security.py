

from __future__ import annotations
from defendai_wozway.types import BaseModel
from defendai_wozway.utils import FieldMetadata, SecurityMetadata
from typing import Optional
from typing_extensions import Annotated, NotRequired, TypedDict


class SecurityTypedDict(TypedDict):
    bearer_auth: NotRequired[str]


class Security(BaseModel):
    bearer_auth: Annotated[
        Optional[str],
        FieldMetadata(
            security=SecurityMetadata(
                scheme=True,
                scheme_type="http",
                sub_type="bearer",
                field_name="Authorization",
            )
        ),
    ] = None
