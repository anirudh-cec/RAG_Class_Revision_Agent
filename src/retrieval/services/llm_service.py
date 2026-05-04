"""
LLM Service for generating responses

Uses MeshAPI for accessing LLMs (both for embeddings and chat).
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import os

from openai import AsyncOpenAI

from src.retrieval.config.settings import get_settings


class LLMService:
    """
    Service for LLM operations via MeshAPI
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=self.settings.MESH_API_KEY,
            base_url=self.settings.MESH_BASE_URL
        )
        self.model = self.settings.LLM_MODEL

    async def generate_response(
        self,
        query: str,
        context: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate response using RAG context

        Args:
            query: User query
            context: List of context documents
            system_prompt: Optional system prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response string
        """
        # Build messages
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # Add context as system message
        context_text = self._format_context(context)
        messages.append({
            "role": "system",
            "content": f"Use the following context to answer the user's question:\n\n{context_text}"
        })

        # Add user query
        messages.append({
            "role": "user",
            "content": query
        })

        # Generate response
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    async def stream_response(
        self,
        query: str,
        context: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        Stream response using RAG context

        Args:
            query: User query
            context: List of context documents
            system_prompt: Optional system prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Response tokens as they are generated
        """
        # Build messages
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # Add context as system message
        context_text = self._format_context(context)
        messages.append({
            "role": "system",
            "content": f"Use the following context to answer the user's question:\n\n{context_text}"
        })

        # Add user query
        messages.append({
            "role": "user",
            "content": query
        })

        # Stream response
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _format_context(self, context: List[Dict[str, str]]) -> str:
        """
        Format context documents for LLM

        Args:
            context: List of context documents

        Returns:
            Formatted context string
        """
        formatted = []

        for idx, doc in enumerate(context, 1):
            content = doc.get("content", "")
            source = doc.get("source", "")

            if source:
                formatted.append(f"[{idx}] Source: {source}\n{content}")
            else:
                formatted.append(f"[{idx}] {content}")

        return "\n\n".join(formatted)

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for query

        Args:
            query: Query string

        Returns:
            Embedding vector
        """
        response = await self.client.embeddings.create(
            model=self.settings.EMBEDDING_MODEL or "text-embedding-3-small",
            input=query
        )

        return response.data[0].embedding
