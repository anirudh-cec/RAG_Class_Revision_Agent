"""
Common types and utilities for models
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel


class Metadata(BaseModel):
    """Common metadata for chunks/documents"""
    source: Optional[str] = None
    source_type: Optional[str] = None  # vtt, code, github
    document_name: Optional[str] = None
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    timestamp: Optional[str] = None
    language: Optional[str] = None
    file_path: Optional[str] = None

    class Config:
        extra = "allow"


class FilterConfig(BaseModel):
    """Configuration for metadata filtering"""
    source_types: Optional[List[str]] = None
    document_names: Optional[List[str]] = None
    date_range: Optional[tuple] = None
    language: Optional[str] = None
    custom_filters: Optional[Dict[str, Any]] = None
