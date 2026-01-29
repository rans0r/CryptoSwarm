"""
Configuration module for CryptoSwarm application.
Loads settings from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "CryptoSwarm"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./cryptoswarm.db"
    
    # Security
    secret_key: str = "change-this-to-a-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # AI APIs
    openai_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    xai_api_base: str = "https://api.x.ai/v1"
    default_ai_provider: str = "openai"  # or "xai"
    
    # Kraken Exchange
    kraken_api_key: Optional[str] = None
    kraken_api_secret: Optional[str] = None
    kraken_testnet: bool = True
    
    # Trading
    max_bots: int = 100
    max_position_size: float = 1000.0  # USD
    min_trade_interval: int = 60  # seconds
    
    # Swarm Evolution
    enable_evolution: bool = True
    mutation_rate: float = 0.1
    crossover_rate: float = 0.3
    fitness_window: int = 30  # days for performance calculation
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
