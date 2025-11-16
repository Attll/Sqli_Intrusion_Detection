from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str
    DB_NAME: str = "sqli_detection"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SQL Injection Detection System"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str
    ADMIN_API_KEY: str
    DEMO_API_KEY: str
    
    # Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-pro"
    
    # ML
    MODEL_PATH: str = "../models"
    DATA_PATH: str = "../data"
    DEFAULT_MODEL: str = "random_forest"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
