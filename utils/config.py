from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:  # pragma: no cover - best effort import
    import yaml
except Exception:  # pragma: no cover - fallback for environments without PyYAML
    yaml = None


@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class PipelineConfig:
    companies: List[str]
    keywords: List[str]


def load_env(path: str | Path = ".env") -> Dict[str, str]:
    """Load key=value pairs from a .env file into the environment."""
    env_path = Path(path)
    data: Dict[str, str] = {}
    if not env_path.exists():
        return data

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"\'')
        os.environ.setdefault(key, value)
        data[key] = value
    return data


def load_yaml_config(path: str | Path) -> Dict:
    """Load a YAML configuration file if PyYAML is available."""
    if yaml is None:
        raise RuntimeError("PyYAML is required to load YAML configuration files")
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def build_database_config(env: Optional[Dict[str, str]] = None) -> DatabaseConfig:
    env = {**os.environ, **(env or {})}
    return DatabaseConfig(
        host=env.get("DB_HOST", "localhost"),
        port=int(env.get("DB_PORT", "3306")),
        user=env.get("DB_USER", "root"),
        password=env.get("DB_PASSWORD", ""),
        database=env.get("DB_NAME", "competitor_intel"),
    )


def build_pipeline_config(config: Dict) -> PipelineConfig:
    companies = config.get("companies", [])
    keywords = config.get("keywords", [])
    if not isinstance(companies, list):
        raise ValueError("companies must be a list")
    if not isinstance(keywords, list):
        raise ValueError("keywords must be a list")
    return PipelineConfig(companies=companies, keywords=keywords)
