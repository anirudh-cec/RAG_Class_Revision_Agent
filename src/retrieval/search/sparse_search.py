"""
Sparse Search Implementation using SPLADE

SPLADE (Sparse Lexical and Expansion Model) provides
document expansion for improved lexical matching.
"""

import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None
    AutoTokenizer = None
    AutoModelForMaskedLM = None

from src.retrieval.search.base import BaseSearch
from src.retrieval.models.responses import SearchResult
from src.retrieval.config.settings import get_settings


class SparseSearch(BaseSearch):
    """
    Sparse search using SPLADE

    SPLADE generates sparse vectors representing
    expanded document/query terms for lexical matching.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        batch_size: int = 32,
        max_length: int = 512,
        device: Optional[str] = None,
        num_workers: int = 4
    ):
        self.settings = get_settings()
        self.model_name = model_name or self.settings.SPLADE_MODEL
        self.batch_size = batch_size
        self.max_length = max_length
        self.num_workers = num_workers

        # Device selection
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Lazy loading
        self._tokenizer = None
        self._model = None
        self._executor = ThreadPoolExecutor(max_workers=num_workers)

        # Index storage (for in-memory index)
        self._index = {}
        self._doc_ids = []

    def _load_model(self):
        """Lazy load model and tokenizer"""
        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForMaskedLM.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()

    def _compute_splade_vector(self, text: str) -> np.ndarray:
        """
        Compute SPLADE vector for text

        Returns sparse vector representation.
        """
        self._load_model()

        # Tokenize
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
            padding=True
        ).to(self.device)

        # Get logits
        with torch.no_grad():
            outputs = self._model(**inputs)
            logits = outputs.logits

        # Apply activation (ReLU + log(1 + x) for SPLADE)
        activations = torch.relu(logits)
        activations = torch.log1p(activations)

        # Max pooling over sequence dimension
        pooled = torch.max(activations, dim=1)[0]

        # Return as numpy array
        return pooled.cpu().numpy().flatten()

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[SearchResult]:
        """
        Perform sparse search using SPLADE

        Note: This implementation uses an in-memory index.
        For production, integrate with a sparse vector database.
        """
        # Compute query vector
        query_vector = await asyncio.get_event_loop().run_in_executor(
            self._executor,
            self._compute_splade_vector,
            query
        )

        # Score all documents in index
        doc_scores = []
        for doc_id, doc_vector in self._index.items():
            # Apply filters if provided
            if filters and not self._matches_filters(doc_id, filters):
                continue

            # Compute score (dot product for sparse vectors)
            score = np.dot(query_vector, doc_vector)
            doc_scores.append((doc_id, score))

        # Sort by score (descending)
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        # Convert to SearchResult
        results = []
        for rank, (doc_id, score) in enumerate(doc_scores[:top_k], start=1):
            # Retrieve document content
            doc_content = self._get_document_content(doc_id)
            doc_metadata = self._get_document_metadata(doc_id)

            result = SearchResult(
                chunk_id=str(doc_id),
                document_id=str(doc_id),
                content=doc_content,
                metadata=doc_metadata,
                score=float(score),
                rank=rank,
                source="sparse"
            )
            results.append(result)

        return results

    def _matches_filters(self, doc_id: str, filters: Dict[str, Any]) -> bool:
        """Check if document matches filters"""
        # Get document metadata
        metadata = self._get_document_metadata(doc_id)

        for key, value in filters.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False

        return True

    def _get_document_content(self, doc_id: str) -> str:
        """Retrieve document content by ID"""
        # This would typically query a database
        # For now, return empty or stored content
        return ""

    def _get_document_metadata(self, doc_id: str) -> Dict[str, Any]:
        """Retrieve document metadata by ID"""
        return {}

    async def batch_search(
        self,
        queries: List[str],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[List[SearchResult]]:
        """Execute multiple searches in parallel"""
        semaphore = asyncio.Semaphore(10)

        async def search_with_limit(query: str) -> List[SearchResult]:
            async with semaphore:
                return await self.search(query, top_k, filters)

        tasks = [search_with_limit(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append([])
            else:
                processed_results.append(result)

        return processed_results

    async def index_document(
        self,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Index a document for sparse search

        Args:
            doc_id: Unique document identifier
            content: Document content
            metadata: Optional metadata
        """
        # Compute SPLADE vector
        vector = await asyncio.get_event_loop().run_in_executor(
            self._executor,
            self._compute_splade_vector,
            content
        )

        # Store in index
        self._index[doc_id] = vector
        self._doc_ids.append(doc_id)

        # Store metadata (in production, use a proper database)
        # self._metadata[doc_id] = metadata or {}
