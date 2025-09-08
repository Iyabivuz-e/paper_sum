"""
Production Configuration Management
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # App Configuration
    app_name: str = "LaughGraph API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Security
    secret_key: str
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # API Keys
    openai_api_key: str
    groq_api_key: Optional[str] = None
    
    # Database Configuration
    chroma_persist_dir: str = "./db/chroma_store"
    collection_name: str = "arxiv_papers"
    
    # Processing Configuration
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    chunk_size: int = 600
    chunk_overlap: int = 50
    max_results_per_search: int = 10
    
    # File Storage
    output_dir: str = "./outputs"
    research_papers_dir: str = "./research_papers"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    # Redis Configuration (for caching and task queue)
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600  # 1 hour
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # Monitoring
    enable_metrics: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    debug: bool = True
    environment: str = "development"
    log_level: str = "DEBUG"
    

class ProductionSettings(Settings):
    debug: bool = False
    environment: str = "production"
    workers: int = 8
    log_level: str = "WARNING"


class TestSettings(Settings):
    debug: bool = True
    environment: str = "testing"
    chroma_persist_dir: str = "./test_db/chroma_store"
    redis_url: str = "redis://localhost:6379/1"


def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    if env == "development":
        return DevelopmentSettings()
    elif env == "testing":
        return TestSettings()
    else:
        return ProductionSettings()
