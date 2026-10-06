from pydantic import BaseModel, Field, field_validator


class CallEndedRequest(BaseModel):
    call_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    duration_secs: int = Field(
        ...,
        ge=0,
    )

    @field_validator("call_id", "status")
    @classmethod
    def strip_and_validate(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be empty")

        return value


class CallResponse(BaseModel):
    call_id: str
    status: str
    duration_secs: int

    class Config:
        from_attributes = True