from __future__ import annotations

import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List


class BaseAgent(ABC):
    """Base class for agents that fetch competitive intelligence."""

    max_retries: int = 3
    backoff_factor: float = 0.5

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def fetch(self, company: str, keywords: List[str]) -> List[Dict]:
        """Fetch raw content for the given company and keywords."""

    def _retry(self, func, *args, **kwargs):
        """Execute *func* with retry and exponential backoff."""
        delay = self.backoff_factor
        for attempt in range(1, self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("Attempt %s failed with %s", attempt, exc)
                if attempt == self.max_retries:
                    raise
                jitter = random.uniform(0, delay)
                time.sleep(delay + jitter)
                delay *= 2
