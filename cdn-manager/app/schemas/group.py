from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    # origin_address: str = Field(
    #     min_length=1,
    #     max_length=255,
    # )


class GroupUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    # origin_address: str | None = Field(
    #     default=None,
    #     min_length=1,
    #     max_length=255,
    # )


class GroupResponse(BaseModel):
    id: int
    name: str
    # origin_address: str

    model_config = {
        "from_attributes": True,
    }