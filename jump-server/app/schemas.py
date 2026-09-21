from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


JumpType = Literal[
    "direct",
    "wildcard",
    "random",
]


JumpMethod = Literal[
    "redirect",
    "js",
    "html",
    "iframe",
]


STATUS_CODES = {
    200,
    301,
    302,
    307,
    308,
    400,
    401,
    403,
    500,
    502,
    503,
    504,
    522,
}


class GroupCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    custom_params: str | None = Field(
        default=None,
        max_length=1000,
    )


    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "group name cannot be empty"
            )

        return value


class GroupUpdate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    custom_params: str | None = Field(
        default=None,
        max_length=1000,
    )
    

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "group name cannot be empty"
            )

        return value


class GroupResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    custom_params: str
    domain_count: int = 0
    created_at: datetime
    updated_at: datetime


class GroupBrief(BaseModel):
    id: int
    name: str
    custom_params: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )



class PoolItem(BaseModel):
    target_domain: str = Field(
        min_length=1,
        max_length=500,
    )

    weight: int = Field(
        default=1,
        ge=1,
    )

    enabled: bool = True

    @field_validator("target_domain")
    @classmethod
    def normalize_target_domain(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "target domain cannot be empty"
            )

        return value


class DomainCreate(BaseModel):
    domain: str = Field(
        min_length=1,
        max_length=255,
    )

    group_id: int

    jump_type: JumpType = "direct"

    jump_method: JumpMethod = "redirect"

    status_code: int = 302

    target_domain: str | None = None

    embedded_code: str | None = None

    enabled: bool = True

    use_group_params: bool = False

    pool: list[PoolItem] = Field(
        default_factory=list
    )

    @field_validator("domain")
    @classmethod
    def normalize_domain(
        cls,
        value: str,
    ) -> str:
        return (
            value
            .strip()
            .lower()
            .rstrip(".")
        )

    @field_validator("target_domain")
    @classmethod
    def normalize_target_domain(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator("embedded_code")
    @classmethod
    def normalize_embedded_code(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator("status_code")
    @classmethod
    def validate_status_code(
        cls,
        value: int,
    ) -> int:

        if value not in STATUS_CODES:
            raise ValueError(
                "invalid status code"
            )

        return value

    @model_validator(mode="after")
    def validate_jump_config(self):

        if self.jump_type in {
            "direct",
            "wildcard",
        }:

            if not self.target_domain:
                raise ValueError(
                    "target_domain is required "
                    "for direct/wildcard"
                )

        if self.jump_type == "random":

            if not self.pool:
                raise ValueError(
                    "pool is required "
                    "for random jump"
                )

        return self


class DomainUpdate(DomainCreate):
    pass


class PoolResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    target_domain: str
    weight: int
    enabled: bool


class DomainResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    domain: str
    group_id: int
    jump_type: str
    jump_method: str
    status_code: int
    target_domain: str | None
    embedded_code: str | None
    enabled: bool
    use_group_params: bool
    group: GroupBrief | None = None
    created_at: datetime
    updated_at: datetime
    pool: list[PoolResponse]


class DomainListResponse(BaseModel):
    items: list[DomainResponse]
    page: int
    page_size: int
    total: int
    pages: int


class BatchIds(BaseModel):
    ids: list[int] = Field(
        min_length=1,
    )


class BatchEnabled(BatchIds):
    enabled: bool


class BatchGroup(BatchIds):
    group_id: int


# 批量搜索 + 批量添加 API schemas
class BatchDomainSearch(BaseModel):
    domains: list[str] = Field(
        min_length=1,
        max_length=1000,
    )

    @field_validator("domains")
    @classmethod
    def normalize_domains(
        cls,
        value: list[str],
    ) -> list[str]:
        result = []

        for item in value:
            domain = (
                item
                .strip()
                .lower()
                .rstrip(".")
            )

            if domain:
                result.append(domain)

        # 去重，保持原顺序
        return list(dict.fromkeys(result))


class BatchDomainCreate(BaseModel):
    domains: list[str] = Field(
        min_length=1,
        max_length=1000,
    )

    group_id: int

    jump_type: JumpType = "direct"

    jump_method: JumpMethod = "redirect"

    status_code: int = 302

    target_domain: str | None = None

    embedded_code: str | None = None

    enabled: bool = True

    use_group_params: bool = False

    pool: list[PoolItem] = Field(
        default_factory=list,
    )

    @field_validator("domains")
    @classmethod
    def normalize_domains(
        cls,
        value: list[str],
    ) -> list[str]:
        result = []

        for item in value:
            domain = (
                item
                .strip()
                .lower()
                .rstrip(".")
            )

            if domain:
                result.append(domain)

        return list(dict.fromkeys(result))

    @model_validator(mode="after")
    def validate_jump_config(self):

        if self.jump_type in {
            "direct",
            "wildcard",
        }:
            if not self.target_domain:
                raise ValueError(
                    "target_domain is required "
                    "for direct/wildcard"
                )

        if self.jump_type == "random":
            if not self.pool:
                raise ValueError(
                    "pool is required "
                    "for random jump"
                )

        return self


class BatchDomainSearchResponse(BaseModel):
    items: list[DomainResponse]
    found: int
    not_found: list[str]





class BatchCreateCheckItem(BaseModel):
    domain: str
    can_create: bool
    reason: str | None = None


class BatchCreateCheckResponse(BaseModel):
    total: int
    can_create: int
    exists: int
    items: list[BatchCreateCheckItem]





class BatchCreateItem(BaseModel):
    domain: str
    success: bool
    reason: str | None = None


class BatchCreateResponse(BaseModel):
    success: bool
    total: int
    created: int
    skipped: int
    items: list[BatchCreateItem]




class AdminLoginRequest(BaseModel):
    password: str


# 批量添加+多目录
class BatchTargetCreateItem(BaseModel):
    domain: str
    target_domain: str
    jump_type: Literal[
        "direct",
        "wildcard",
    ]


class BatchTargetCreateRequest(BaseModel):
    items: list[BatchTargetCreateItem]

    group_id: int | None = None

    jump_method: JumpMethod = "redirect"

    status_code: int = 302

    enabled: bool = True

    use_group_params: bool = False

    embedded_code: str | None = None




# 批量更新目标完整地址
class BatchTargetUpdate(BaseModel):

    old_target_domain: str = Field(
        min_length=1,
        max_length=500,
    )

    new_target_domain: str = Field(
        min_length=1,
        max_length=500,
    )

    @field_validator(
        "old_target_domain",
        "new_target_domain",
    )
    @classmethod
    def normalize_target_domain(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "target domain cannot be empty"
            )

        return value


class BatchTargetUpdateResponse(BaseModel):

    success: bool
    updated: int



# 批量更新状态码
class BatchStatus(BatchIds):

    status_code: int

    @field_validator("status_code")
    @classmethod
    def validate_status_code(
        cls,
        value: int,
    ) -> int:

        if value not in STATUS_CODES:
            raise ValueError(
                "invalid status code"
            )

        return value



## 批量修改目标顶级域名
class BatchReplaceTargetDomainRequest(BaseModel):
    domain_ids: list[int]
    old_domain: str
    new_domain: str


# ==============================
# 批量启用|禁用分组参数
# ==============================
class BatchGroupParamsRequest(BaseModel):
    domain_ids: list[int]
    use_group_params: bool