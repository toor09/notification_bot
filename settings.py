import sys
from typing import List

from pydantic import AnyHttpUrl, BaseSettings, validator

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    DVMN_API_TOKEN: str
    DVMN_API_URL: AnyHttpUrl
    DVMN_API_URI_REVIEWS: str
    DVMN_API_URI_REVIEWS_LONG_POLLING: str
    READ_TIMEOUT: int = 180
    TIMEOUT: int = 10
    RETRY_COUNT: int = 5
    STATUS_FORCE_LIST: str = "429,500,502,503,504"
    ALLOWED_METHODS: str = "HEAD,GET,OPTIONS"
    TG_BOT_TOKEN: str
    TG_CHAT_ID: str
    LOGGING_LEVEL: str = "WARNING"

    @validator("STATUS_FORCE_LIST")
    def status_force_list(cls, v: str) -> List[int]:
        if isinstance(v, str):
            return [int(_v.strip()) for _v in v.split(",")]

    @validator("ALLOWED_METHODS")
    def allowed_methods(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [_v.strip() for _v in v.split(",")]

    @validator("LOGGING_LEVEL")
    def logging_levels(cls, v: str) -> str:
        if v.upper() not in LEVELS:
            raise ValueError(
                f"The value is not in the list of required: {LEVELS}"
            )
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": Settings().LOGGING_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": sys.stderr,
        },
        "rotating_to_file": {
            "level": Settings().LOGGING_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "notification_bot.log",
            "maxBytes": 10000,
            "backupCount": 10,
        },
        "telegram_bot": {
            "class": "utils.TelegramLogsHandler",
            "token": Settings().TG_BOT_TOKEN,
            "chat_id": Settings().TG_CHAT_ID,
            "level": Settings().LOGGING_LEVEL,
            "formatter": "standard",
        }
    },
    "loggers": {
        "main": {
            "handlers": ["default", "rotating_to_file", "telegram_bot"],
            "level": Settings().LOGGING_LEVEL,
            "propagate": True
        }
    }
}
