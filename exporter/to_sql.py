from __future__ import annotations

from typing import Dict, Iterable

from utils.db import Database


def export_to_sql(database: Database, records: Iterable[Dict]) -> None:
    """Persist cleaned records into the database."""
    for record in records:
        database.insert_cleaned_content(record)
