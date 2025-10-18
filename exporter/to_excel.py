from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

try:  # pragma: no cover - optional dependency
    import pandas as pd
except Exception:  # pragma: no cover - fallback when pandas missing
    pd = None


def export_to_excel(records: Sequence[Dict], path: str | Path) -> Path:
    """Persist records to an Excel compatible file."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if pd is not None:
        frame = pd.DataFrame(list(records))
        frame.to_excel(destination, index=False)
    else:  # pragma: no cover - fallback behaviour
        destination.write_text(json.dumps(list(records), indent=2), encoding="utf-8")
    return destination
