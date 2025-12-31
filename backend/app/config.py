"""
Application Configuration
Loads environment variables and provides settings to the application.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://escalation_user:escalation_pass@localhost:5432/escalation_tracker"
    
    # JWT Authentication
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI Integration
    gemini_api_key: str = ""
    
    # Email Ingestion
    imap_server: str = "outlook.office365.com"
    imap_port: int = 993
    imap_use_ssl: bool = True
    imap_email: str = ""
    imap_password: str = ""
    imap_folder: str = "INBOX"
    imap_processed_folder: str = "Processed"
    mock_email_ingestion: bool = True
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Application
    app_name: str = "Escalation Tracker"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
