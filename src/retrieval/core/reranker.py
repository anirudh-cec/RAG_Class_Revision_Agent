"""
Cross-Encoder Reranker

Uses cross-encoder/ms-marco-MiniLM-L6-v2 from HuggingFace
for final reranking of retrieved documents.
"""

import asyncio
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from src.retrieval.models.responses import SearchResult
from src.retrieval.config.settings import get_settings


class CrossEncoderReranker:
    """
    Cross-encoder reranker using ms-marco-MiniLM-L6-v2
    """

    def __init__(
        self,
        model_name: str = None,
        batch_size: int = None,
        max_length: int = None,
        device: Optional[str] = None,
        num_workers: int = 4
    ):
        self.settings = get_settings()
        self.model_name = model_name or self.settings.RERANKER_MODEL
        self.batch_size = batch_size or self.settings.RERANKER_BATCH_SIZE
        self.max_length = max_length or self.settings.RERANKER_MAX_LENGTH
        self.num_workers = num_workers

        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self._tokenizer = None
        self._model = None
        self._executor = ThreadPoolExecutor(max_workers=num_workers)

    def _load_model(self):
        """Lazy load model and tokenizer"""
        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name
            )
            self._model.to(self.device)
            self._model.eval()

    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: int = 5
    ) -> List[SearchResult]:
        """Rerank search results using cross-encoder"""
        if not results:
            return []

        self._load_model()

        # Prepare query-document pairs
        pairs = []
        for result in results:
            doc_text = result.content
            if result.metadata and "title" in result.metadata:
                doc_text = f"{result.metadata['title']}\n{doc_text}"
            pairs.append((query, doc_text))

        # Score all pairs in batches
        scores = await self._score_pairs(pairs)

        # Create reranked results
        reranked = []
        for idx, (result, score) in enumerate(zip(results, scores)):
            reranked_result = SearchResult(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                content=result.content,
                metadata=result.metadata,
                score=result.score,
                rank=result.rank,
                source=result.source,
                reranked_score=float(score),
                reranked_rank=0
            )
            reranked.append(reranked_result)

        # Sort by reranked score (descending)
        reranked.sort(key=lambda x: x.reranked_score, reverse=True)

        # Assign reranked ranks and limit to top_k
        final_results = []
        for rank, result in enumerate(reranked[:top_k], start=1):
            result.reranked_rank = rank
            final_results.append(result)

        return final_results

    async def _score_pairs(self, pairs: List[tuple]) -> List[float]:
        """Score query-document pairs using cross-encoder in batches"""
        all_scores = []

        for i in range(0, len(pairs), self.batch_size):
            batch = pairs[i:i + self.batch_size]

            scores = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                self._score_batch,
                batch
            )
            all_scores.extend(scores)

        return all_scores

    def _score_batch(self, batch: List[tuple]) -> List[float]:
        """Score a batch of pairs (runs in thread pool)"""
        features = self._tokenizer(
            [pair[0] for pair in batch],
            [pair[1] for pair in batch],
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )

        features = {k: v.to(self.device) for k, v in features.items()}

        with torch.no_grad():
            scores = self._model(**features).logits.squeeze(-1)

        if scores.dim() == 0:
            return [scores.item()]
        return scores.cpu().tolist()
