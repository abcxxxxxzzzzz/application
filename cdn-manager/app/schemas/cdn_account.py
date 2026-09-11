from pydantic import BaseModel, Field


class CDNAccountCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    account_id: str = Field(
        min_length=1,
        max_length=64,
    )

    api_token: str = Field(
        min_length=1,
    )


class CDNAccountUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    account_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
    )

    api_token: str | None = Field(
        default=None,
        min_length=1,
    )


class CDNAccountResponse(BaseModel):
    id: int
    name: str
    account_id: str
    token_configured: bool

    model_config = {
        "from_attributes": True,
    }