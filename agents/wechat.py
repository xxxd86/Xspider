from __future__ import annotations

import logging
from typing import Dict, List

from .base import BaseAgent


class WeChatAgent(BaseAgent):
    """Placeholder agent that mocks fetching data from WeChat."""

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger("WeChatAgent")

    def fetch(self, company: str, keywords: List[str]) -> List[Dict]:
        def _simulate_fetch():
            self.logger.debug("Fetching WeChat posts for %s with keywords %s", company, keywords)
            return [
                {
                    "source": "wechat",
                    "company": company,
                    "keyword": keyword,
                    "content": f"Simulated post about {company} and {keyword}",
                }
                for keyword in keywords
            ]

        return self._retry(_simulate_fetch)
