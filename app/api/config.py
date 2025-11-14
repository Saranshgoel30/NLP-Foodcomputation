"""
Configuration management using pydantic-settings
Loads from environment variables and .env file
"""
from functools import lru_cache
from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    cors_origins: str = "http://localhost:3000"
    
    # Translation
    translation_provider: Literal['indicTrans2', 'marianMT', 'api'] = 'marianMT'
    translation_endpoint: str = ""
    
    # STT
    stt_provider: Literal['whisper', 'vosk'] = 'whisper'
    stt_model_name: str = 'small'
    stt_model_path: str = ""
    
    # Typesense (Primary Search Engine)
    typesense_host: str = "localhost"
    typesense_port: int = 8108
    typesense_protocol: str = "http"
    typesense_api_key: str = "xyz"
    typesense_enabled: bool = True  # Typesense is the primary search engine
    
    # Search Strategy
    search_strategy: Literal['semantic', 'keyword', 'hybrid'] = 'hybrid'
    hybrid_semantic_weight: float = 0.7  # Weight for semantic vs keyword in hybrid mode
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: Literal['json', 'console'] = 'json'
    
    # External APIs (Optional - for future enrichment)
    food_graph_api_url: str = ""
    food_graph_api_key: str = ""
    
    # Feature Flags
    enable_nutrition_enrichment: bool = True
    enable_ingredient_standardization: bool = True
    enable_autocomplete: bool = True
    
    # Performance
    nutrition_enrichment_timeout: int = 5000  # milliseconds
    enrichment_batch_size: int = 10  # How many recipes to enrich
    
    # Security
    secret_key: str = "change-this-secret-key"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(',')]
    
    @property
    def graphdb_endpoint(self) -> str:
        """Full SPARQL endpoint URL"""
        return f"{self.graphdb_url}/repositories/{self.graphdb_repository}"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
