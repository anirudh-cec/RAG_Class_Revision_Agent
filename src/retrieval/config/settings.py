"""
Pydantic Settings for Retrieval Pipeline
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=4, env="API_WORKERS")

    # AstraDB Configuration
    ASTRA_DB_API_ENDPOINT: str = Field(..., env="ASTRA_DB_API_ENDPOINT")
    ASTRA_DB_TOKEN: str = Field(..., env="ASTRA_DB_TOKEN")
    ASTRA_DB_COLLECTION: str = Field(default="document_chunks", env="ASTRA_DB_COLLECTION")

    # MeshAPI Configuration (LLM)
    MESH_API_KEY: str = Field(..., env="MESH_API_KEY")
    MESH_BASE_URL: str = Field(default="https://api.meshapi.ai/v1", env="MESH_BASE_URL")
    LLM_MODEL: str = Field(default="openai/gpt-4o-mini", env="LLM_MODEL")

    # Embedding Configuration
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    EMBEDDING_DIMENSION: int = Field(default=1536, env="EMBEDDING_DIMENSION")

    # SPLADE Configuration (Sparse)
    SPLADE_MODEL: str = Field(
        default="naver/splade-cocondenser-ensembledistil",
        env="SPLADE_MODEL"
    )

    # Reranker Configuration
    RERANKER_MODEL: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L6-v2",
        env="RERANKER_MODEL"
    )
    RERANKER_BATCH_SIZE: int = Field(default=32, env="RERANKER_BATCH_SIZE")
    RERANKER_MAX_LENGTH: int = Field(default=512, env="RERANKER_MAX_LENGTH")

    # RRF Configuration
    RRF_K: int = Field(default=60, env="RRF_K")

    # Search Configuration
    DEFAULT_TOP_K: int = Field(default=5, env="DEFAULT_TOP_K")
    DENSE_SEARCH_K: int = Field(default=50, env="DENSE_SEARCH_K")
    SPARSE_SEARCH_K: int = Field(default=50, env="SPARSE_SEARCH_K")
    RERANK_CANDIDATES: int = Field(default=20, env="RERANK_CANDIDATES")

    # Performance
    MAX_CONCURRENT_SEARCHES: int = Field(default=10, env="MAX_CONCURRENT_SEARCHES")
    BATCH_SIZE: int = Field(default=32, env="BATCH_SIZE")

    # Caching
    CACHE_ENABLED: bool = Field(default=True, env="CACHE_ENABLED")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment"""
    global _settings
    _settings = Settings()
    return _settings
