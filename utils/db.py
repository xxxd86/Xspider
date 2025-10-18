from __future__ import annotations

import logging
from typing import Dict, Iterable, Optional

from .config import DatabaseConfig

try:  # pragma: no cover - optional dependency
    from sqlalchemy import MetaData, Table, create_engine, insert
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import SQLAlchemyError
except Exception:  # pragma: no cover - fallback when SQLAlchemy missing
    MetaData = Table = create_engine = insert = Engine = SQLAlchemyError = None


class Database:
    """Lightweight database helper around SQLAlchemy with in-memory fallback."""

    def __init__(self, config: DatabaseConfig, url: Optional[str] = None) -> None:
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._memory_store: Dict[str, list] = {
            "company_info": [],
            "content_raw": [],
            "content_cleaned": [],
        }
        self.engine: Optional[Engine] = None
        self.metadata: Optional[MetaData] = None

        if create_engine is None:
            self.logger.info("SQLAlchemy not available; using in-memory store")
            return

        url = url or self._build_mysql_url()
        try:
            self.engine = create_engine(url, future=True)
            self.metadata = MetaData()
            try:
                self.metadata.reflect(bind=self.engine)
            except SQLAlchemyError:  # pragma: no cover - DB may not be accessible
                self.metadata = None
        except SQLAlchemyError:  # pragma: no cover - connection failure fallback
            self.logger.warning("Database connection failed; using in-memory store")
            self.engine = None

    def _build_mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.config.user}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )

    # insertion helpers -------------------------------------------------
    def insert_company_info(self, record: Dict) -> None:
        self._insert("company_info", record)

    def insert_raw_content(self, record: Dict) -> None:
        self._insert("content_raw", record)

    def insert_cleaned_content(self, record: Dict) -> None:
        self._insert("content_cleaned", record)

    # internal helpers --------------------------------------------------
    def _insert(self, table_name: str, record: Dict) -> None:
        if self.engine is None or self.metadata is None:
            self._memory_store.setdefault(table_name, []).append(record)
            return

        table = self._get_table(table_name)
        if table is None:
            self._memory_store.setdefault(table_name, []).append(record)
            return

        try:  # pragma: no cover - interacts with external DB
            with self.engine.begin() as connection:
                connection.execute(insert(table).values(**record))
        except SQLAlchemyError:
            self.logger.exception("Failed to insert into %s; falling back to memory store", table_name)
            self._memory_store.setdefault(table_name, []).append(record)

    def _get_table(self, table_name: str) -> Optional[Table]:
        if self.metadata is None:
            return None
        if table_name in self.metadata.tables:
            return self.metadata.tables[table_name]
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            return table
        except SQLAlchemyError:  # pragma: no cover - table may not exist yet
            return None

    # convenience accessors for tests ----------------------------------
    def dump_memory_store(self, table_name: str) -> Iterable[Dict]:
        return list(self._memory_store.get(table_name, []))
