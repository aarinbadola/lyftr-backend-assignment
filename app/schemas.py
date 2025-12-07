# app/schemas.py
from pydantic import BaseModel, Field, field_validator
import re

E164_RE = re.compile(r"^\+\d+$")


class WebhookMessage(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_: str = Field(..., alias="from")
    to: str
    ts: str
    text: str | None = None

    @field_validator("from_", "to", mode="after")
    def check_e164(cls, v: str) -> str:
        if not isinstance(v, str) or not E164_RE.match(v):
            raise ValueError("must be E.164-like (+digits)")
        return v

    @field_validator("ts", mode="after")
    def check_ts_z(cls, v: str) -> str:
        if not v or not isinstance(v, str) or not v.endswith("Z"):
            raise ValueError("ts must be ISO-8601 UTC string with Z suffix")
        return v

    @field_validator("text", mode="after")
    def check_text_len(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 4096:
            raise ValueError("text too long (max 4096)")
        return v

    model_config = {
        "populate_by_name": True,  
    }

