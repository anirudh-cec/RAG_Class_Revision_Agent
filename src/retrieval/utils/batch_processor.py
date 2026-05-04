"""
Batch processing utilities for parallel operations
"""

import asyncio
from typing import List, TypeVar, Callable, Any
from concurrent.futures import ThreadPoolExecutor

T = TypeVar('T')
R = TypeVar('R')


class BatchProcessor:
    """
    Process items in batches with parallel execution
    """

    def __init__(
        self,
        batch_size: int = 32,
        max_workers: int = 4,
        use_async: bool = True
    ):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.use_async = use_async
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process(
        self,
        items: List[T],
        process_func: Callable[[T], R],
        use_async: bool = None
    ) -> List[R]:
        """
        Process items in batches

        Args:
            items: List of items to process
            process_func: Function to apply to each item
            use_async: Whether to use async processing

        Returns:
            List of results
        """
        use_async = use_async if use_async is not None else self.use_async

        results = []

        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]

            if use_async:
                # Process batch asynchronously
                batch_results = await self._process_batch_async(batch, process_func)
            else:
                # Process batch in thread pool
                batch_results = await self._process_batch_threaded(batch, process_func)

            results.extend(batch_results)

        return results

    async def _process_batch_async(
        self,
        batch: List[T],
        process_func: Callable[[T], R]
    ) -> List[R]:
        """Process batch using async functions"""
        tasks = [process_func(item) for item in batch]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_batch_threaded(
        self,
        batch: List[T],
        process_func: Callable[[T], R]
    ) -> List[R]:
        """Process batch using thread pool"""
        loop = asyncio.get_event_loop()

        results = []
        for item in batch:
            try:
                result = await loop.run_in_executor(
                    self._executor,
                    process_func,
                    item
                )
                results.append(result)
            except Exception as e:
                results.append(e)

        return results

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._executor.shutdown(wait=True)


def create_batch_processor(
    batch_size: int = 32,
    max_workers: int = 4
) -> BatchProcessor:
    """Factory function to create BatchProcessor"""
    return BatchProcessor(
        batch_size=batch_size,
        max_workers=max_workers
    )
