from pydantic import BaseModel, Field


class DomainCreate(BaseModel):
    domain: str = Field(
        min_length=1,
        max_length=255,
    )

    cdn_account_id: int

    # desired_cdn: str = Field(
    #     default="cf",
    #     min_length=1,
    #     max_length=32,
    # )

    enabled: bool = True


class DomainUpdate(BaseModel):
    domain: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    cdn_account_id: int | None = None

    desired_cdn: str | None = Field(
        default=None,
        min_length=1,
        max_length=32,
    )

    enabled: bool | None = None


class DomainResponse(BaseModel):
    id: int
    group_id: int
    cdn_account_id: int
    domain_zone_id: str
    domain: str
    desired_cdn: str | None
    enabled: bool
    switch_remark: str | None

    model_config = {
        "from_attributes": True,
    }



class DomainSwitchRequest(BaseModel):
    cdn: str = Field(
        min_length=1,
        max_length=32,
    )

    remark: str | None = Field(
        default=None,
        max_length=500,
    )