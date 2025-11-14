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
    
    # GraphDB
    graphdb_url: str = "http://16.170.211.162:7200"
    graphdb_repository: str = "mmfood_hackathon"
    graphdb_named_graph: str = "http://172.31.34.244/fkg"
    graphdb_username: str = ""
    graphdb_password: str = ""
    graphdb_timeout: int = 30  # Increased to 30 seconds for complex queries
    
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
    
    # Typesense (Vector Search)
    typesense_host: str = "localhost"
    typesense_port: int = 8108
    typesense_protocol: str = "http"
    typesense_api_key: str = "xyz"
    typesense_enabled: bool = False  # Enable when Typesense is set up
    
    # Search Strategy
    search_strategy: Literal['graphdb', 'typesense', 'hybrid'] = 'graphdb'  # Can switch to 'hybrid' later
    hybrid_semantic_weight: float = 0.7  # Weight for semantic vs keyword in hybrid mode
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: Literal['json', 'console'] = 'json'
    
    # External APIs
    existing_api_base: str = "http://16.170.211.162:8001"
    food_graph_api: str = "http://16.170.211.162:8002"
    
    # Food Graph API (Nutrition & Ingredients)
    food_graph_api_url: str = "http://16.170.211.162:8001"
    food_graph_api_key: str = ""  # Optional, only for admin endpoints
    
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
