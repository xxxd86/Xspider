from __future__ import annotations

from typing import Dict, Iterable, List


REQUIRED_FIELDS = {"source", "company", "content"}


def filter_invalid(records: Iterable[Dict]) -> List[Dict]:
    """Filter out records missing required fields."""
    valid: List[Dict] = []
    for record in records:
        if not REQUIRED_FIELDS.issubset(record):
            continue
        if not str(record.get("content", "")).strip():
            continue
        valid.append(record)
    return valid
