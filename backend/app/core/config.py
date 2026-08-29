from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Razorpay RiskGuard'
    VERSION: str = '0.1.0'
    API_V1_STR: str = '/v1'
    ENVIRONMENT: str = 'development'
    
    # Redis
    REDIS_URL: str = 'redis://localhost:6379/0'
    
    # Postgres
    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = 'riskguard'
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/riskguard'
    
    # LLM Settings (for Risk Explanation Agent)
    OPENAI_API_KEY: str = ''
    ANTHROPIC_API_KEY: str = ''
    GEMINI_API_KEY: str = ''
    LLM_PROVIDER: str = 'mock'  # 'openai' | 'gemini' | 'anthropic' | 'mock'
    
    # Uncertainty & Threshold Hyperparameters
    DEFAULT_DECLINE_THRESHOLD: float = 0.80
    DEFAULT_STEP_UP_THRESHOLD: float = 0.30
    BANDIT_EPSILON: float = 0.10
    BANDIT_SMOOTHING_ALPHA: float = 0.30
    BANDIT_MIN_SAMPLES: int = 50
    BANDIT_FLOOR_THRESHOLD: float = 0.40
    BANDIT_CEILING_THRESHOLD: float = 0.95
    
    # CORS
    CORS_ORIGINS: List[str] = ['*']

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')


settings = Settings()
