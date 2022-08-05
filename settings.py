from typing import List

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    DVMN_API_TOKEN: str
    DVMN_API_URL: AnyHttpUrl
    DVMN_API_URI_REVIEWS: str
    DVMN_API_URI_REVIEWS_LONG_POLLING: str
    TIMEOUT: int = 10
    RETRY_COUNT: int = 5
    STATUS_FORCE_LIST: str = "429,500,502,503,504"
    ALLOWED_METHODS: str = "HEAD,GET,OPTIONS"

    @validator("STATUS_FORCE_LIST")
    def status_force_list(cls, v: str) -> List[int]:
        if isinstance(v, str):
            return [int(_v.strip()) for _v in v.split(",")]

    @validator("ALLOWED_METHODS")
    def allowed_methods(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [_v.strip() for _v in v.split(",")]

    class Config:
        case_sensitive = True
        env_file = ".env"
