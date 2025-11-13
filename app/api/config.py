from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    HUBSPOT_ACCESS_TOKEN: str
    HUBSPOT_TIMEOUT: int = 10
    
    APP_NAME: str = "CRM Integration API"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()