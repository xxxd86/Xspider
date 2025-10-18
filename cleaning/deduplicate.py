from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


def deduplicate(records: Iterable[Dict]) -> List[Dict]:
    """Remove duplicate records based on source+company+content."""
    seen: set[Tuple[str, str, str]] = set()
    unique: List[Dict] = []
    for record in records:
        key = (
            str(record.get("source")),
            str(record.get("company")),
            str(record.get("content")),
        )
        if key not in seen:
            seen.add(key)
            unique.append(record)
    return unique
