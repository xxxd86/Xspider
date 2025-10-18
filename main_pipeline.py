from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Iterable, List

from agents.wechat import WeChatAgent
from cleaning.deduplicate import deduplicate
from cleaning.filter_invalid import filter_invalid
from cleaning.normalise import normalize_content
from exporter.report import generate_report
from exporter.to_excel import export_to_excel
from exporter.to_sql import export_to_sql
from utils.config import (
    build_database_config,
    build_pipeline_config,
    load_env,
    load_yaml_config,
)
from utils.db import Database


def expand_keywords(base_keywords: Iterable[str], company: str) -> List[str]:
    unique = {keyword.strip() for keyword in base_keywords if keyword}
    unique.add(company)
    return sorted(unique)


def run_pipeline(config_path: str | Path = "config/pipeline.yaml") -> Dict[str, List[Dict]]:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logger = logging.getLogger("main_pipeline")

    logger.info("Loading environment and configuration")
    env_data = load_env()
    pipeline_cfg = build_pipeline_config(load_yaml_config(config_path))
    db_config = build_database_config(env_data)

    database = Database(db_config)
    agent = WeChatAgent()

    raw_records: List[Dict] = []
    cleaned_records: List[Dict] = []

    for company in pipeline_cfg.companies:
        logger.info("Processing company %s", company)
        database.insert_company_info({"name": company})
        keywords = expand_keywords(pipeline_cfg.keywords, company)
        fetched = agent.fetch(company, keywords)
        raw_records.extend(fetched)
        for record in fetched:
            database.insert_raw_content(record)

    logger.info("Running cleaning steps")
    normalised = normalize_content(raw_records)
    filtered = filter_invalid(normalised)
    cleaned_records = deduplicate(filtered)

    for record in cleaned_records:
        database.insert_cleaned_content(record)

    logger.info("Exporting results")
    export_to_excel(cleaned_records, Path("output/cleaned_records.xlsx"))
    export_to_sql(database, cleaned_records)

    report = generate_report(cleaned_records)
    report_path = Path("output/report.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    logger.info("Report written to %s", report_path)

    return {"raw": raw_records, "cleaned": cleaned_records}


if __name__ == "__main__":  # pragma: no cover
    run_pipeline()
