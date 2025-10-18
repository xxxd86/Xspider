from __future__ import annotations

from typing import Dict, List


def normalize_content(records: List[Dict]) -> List[Dict]:
    """Normalise raw text fields (stub implementation)."""
    normalised = []
    for record in records:
        text = record.get("content", "")
        if isinstance(text, str):
            normalised.append({**record, "content": " ".join(text.split())})
        else:
            normalised.append(record)
    return normalised
