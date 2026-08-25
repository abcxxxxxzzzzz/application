import yaml
from pathlib import Path
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.yaml"


def load_config():
    if not CONFIG_FILE.exists():
        return {}

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return yaml.safe_load(f) or {}


class Settings(BaseSettings):
    base_url: str = "https://www.kk.yun"

    api_url: str = ""

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/138 Safari/537.36"
    )

    timeout: int = 30

    interval: int = 300

    poll_interval: int = 2

    projects: list[dict] = []

    log_dir: str = "./logs"

    alarm_threshold: int = 5

    alarm_cooldown: int = 300

    alarm_confirm_times: int = 2

    alarm_confirm_interval: int = 5

    telegram_enable: bool = False

    telegram_bot_token: str = ""

    telegram_chat_id: str = ""

    timezone: str = "Asia/Shanghai"

    class Config:
        extra = "ignore"


config = load_config()

settings = Settings(
    **config
)

if not settings.api_url:
    settings.api_url = (
        settings.base_url
        + "/api/kkyun/measurements"
    )