from pydantic import BaseModel, Field


class DomainCDNTargetCreate(BaseModel):
    cdn: str = Field(
        min_length=1,
        max_length=32,
    )

    cname: str = Field(
        min_length=1,
        max_length=255,
    )

    proxied: int = Field(
      ge=0,
      le=1,
    )


class DomainCDNTargetUpdate(BaseModel):
    cdn: str | None = Field(
        default=None,
        min_length=1,
        max_length=32,
    )

    cname: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    proxied: int = Field(
      ge=0,
      le=1,
    )


class DomainCDNTargetResponse(BaseModel):
    id: int
    domain_id: int
    cdn: str
    cname: str
    proxied: int

    model_config = {
        "from_attributes": True,
    }