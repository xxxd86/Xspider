from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable


def generate_report(records: Iterable[Dict]) -> str:
    """Generate a simple summary report of records by company."""
    counter = Counter(record.get("company", "unknown") for record in records)
    lines = ["Competitor Intelligence Summary"]
    for company, count in sorted(counter.items()):
        lines.append(f"- {company}: {count} items")
    return "\n".join(lines)
