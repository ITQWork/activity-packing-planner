from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Activity Packing Planner"
    DATABASE_URL: str = "sqlite:///./packing_planner.db"
    
    # JWT Settings (placeholders for now)
    SECRET_KEY: str = "your-secret-key-for-dev-only"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
