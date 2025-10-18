from pathlib import Path

from exporter.report import generate_report
from exporter.to_excel import export_to_excel
from exporter.to_sql import export_to_sql
from utils.config import DatabaseConfig
from utils.db import Database


def test_export_to_excel_creates_file(tmp_path):
    records = [{"company": "Acme", "content": "Data", "source": "wechat"}]
    destination = export_to_excel(records, tmp_path / "records.xlsx")
    assert destination.exists()


def test_generate_report_counts_records():
    records = [{"company": "Acme"}, {"company": "Beta"}, {"company": "Acme"}]
    report = generate_report(records)
    assert "Acme: 2" in report
    assert "Beta: 1" in report


def test_export_to_sql_uses_database_memory_store():
    db = Database(DatabaseConfig(host="localhost", port=3306, user="u", password="p", database="d"))
    records = [{"company": "Acme", "content": "Data", "source": "wechat"}]
    export_to_sql(db, records)
    assert list(db.dump_memory_store("content_cleaned")) == records
