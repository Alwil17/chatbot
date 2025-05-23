# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    ENV_NAME: str = "alwil17"
    AWS_REGION_NAME: str = ""
    DYNAMO_TABLE: str = ""
    AWS_PROFILE: str = ""
    MISTRAL_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBHOOK_PATH: str = "/telegram/webhook"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


@lru_cache
def get_settings():
    return settings


env_vars = get_settings()
