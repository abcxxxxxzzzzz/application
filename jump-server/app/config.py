from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Jump Server"
    debug: bool = False

    mysql_host: str = "mysql"
    mysql_port: int = 3306
    mysql_user: str = "jump"
    mysql_password: str = "jump"
    mysql_database: str = "jump"

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    cache_ttl: int = 300

    admin_password: str = "123456"
    admin_token: str = "12345QOIWEQOWEJQLWEJQW"
    admin_cookie_name: str = "admin_auth"
    admin_cookie_expire: int = 86400

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def mysql_url(self) -> str:
        return (
            "mysql+asyncmy://"
            f"{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}"
            f"/{self.mysql_database}"
            "?charset=utf8mb4"
        )

    @property
    def redis_url(self) -> str:
        auth = ""

        if self.redis_password:
            auth = f":{self.redis_password}@"

        return (
            f"redis://{auth}"
            f"{self.redis_host}:{self.redis_port}"
            f"/{self.redis_db}"
        )


settings = Settings()