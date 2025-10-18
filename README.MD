# Xspider Competitor Intelligence Pipeline

## Project Overview
Xspider automates the collection of competitor intelligence data, normalizes it, and
stores the curated results in MySQL while publishing analyst-friendly Excel
reports. The project orchestrates multiple scraping and enrichment tasks,
normalizes the results, and produces executive summaries so that commercial teams
have fresh insight into their market landscape.

The primary orchestration entry point is `main_pipeline.py`, which loads
configuration from `.env` and YAML files, connects to your MySQL instance, and
coordinates the ETL steps defined across the modules in this repository. The
pipeline produces three major artifacts for each run:

- Structured database tables under the `competitor_intel` schema in MySQL
- Downloadable Excel workbooks with raw and curated datasets (default location:
  `reports/`)
- Textual summary exports (default location: `output/summaries/`)

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python 3.10+ | Earlier versions are not tested. The codebase uses
  type-annotation features that were stabilized in Python 3.10. |
| MySQL 8.0+ | A running instance is required for persistence. You need a
  database user with permissions to create schemas, tables, and run stored
  procedures. |
| System libraries | Ensure the `libmysqlclient` development headers are
  available before installing dependencies (e.g., `sudo apt-get install
  default-libmysqlclient-dev` on Debian/Ubuntu). |

The Python dependencies are recorded in `requirements.txt`. Install them inside a
virtual environment to avoid polluting your global interpreter state:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If you use Poetry, you can alternatively run `poetry install` inside the
repository, which reads the same dependency set from `pyproject.toml`.

## Configuration

### `.env` file

Create a `.env` file at the project root so `python-dotenv` (loaded from
`main_pipeline.py`) can inject sensitive values into the process environment. The
minimum configuration includes:

```dotenv
# Database
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=xspider
DB_PASSWORD=super-secret
DB_NAME=competitor_intel

# Optional service integrations
OPENAI_API_KEY=sk-...
SCRAPER_API_KEY=...
EMAIL_NOTIFICATIONS=true
```

Adjust the credentials to match your deployment. Any additional environment keys
referenced in the codebase (for example, API credentials for data providers or
SMTP settings for notifications) should also be defined here.

### YAML configuration files

The pipeline uses YAML files located in `config/` to describe company coverage
and keyword tracking rules. Update these files to match your monitoring needs:

- `config/companies.yaml` – List each company to be monitored along with
  metadata such as company name, website, primary contacts, and tags. Example:

  ```yaml
  companies:
    - id: acme
      name: Acme Corporation
      website: https://www.acme.com
      industry: manufacturing
      notes: Top competitor in North America
    - id: globex
      name: Globex
      website: https://www.globex.com
      industry: energy
  ```

- `config/keywords.yaml` – Define topic clusters and search terms that the
  scraper should use. Example:

  ```yaml
  keyword_groups:
    - topic: product launches
      include:
        - "launch"
        - "release"
        - "beta"
      exclude:
        - "job"
        - "hiring"
    - topic: funding
      include:
        - "funding"
        - "investment"
        - "seed round"
  ```

- `config/settings.yaml` – (optional) Override operational parameters such as
  crawl cadence, concurrency, rate limits, and file output directories. Provide a
  section for each subsystem that `main_pipeline.py` expects, for example:

  ```yaml
  pipeline:
    run_id: 2024-04-01
    output_dir: reports
    summaries_dir: output/summaries
    max_retries: 3
  scraping:
    concurrent_jobs: 5
    timeout_seconds: 30
  enrichment:
    enable_llm_summary: true
    llm_model: gpt-4
  ```

Commit sanitized versions of these files to source control (for structure
reference) and keep secrets exclusively in `.env`.

## Database Initialization

The SQL schema lives in `db/create_competitor_intel_schema.sql`. Execute it once
before running the pipeline to set up tables, views, and stored procedures. You
can initialize the schema from your terminal with the MySQL client:

```bash
mysql \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --user="$DB_USER" \
  --password="$DB_PASSWORD" \
  < db/create_competitor_intel_schema.sql
```

Replace the environment variables with actual values if you are not using a
shell that performs substitution. Re-running the script is idempotent; it drops
and recreates objects only when necessary. After execution, inspect the tables to
confirm that the schema is ready:

```bash
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" \
  -e "SHOW TABLES FROM competitor_intel;"
```

## Running the Pipeline

1. Activate your virtual environment and ensure dependencies are installed.
2. Load environment variables (either through `.env` or your shell).
3. Run the pipeline, optionally passing the path to your YAML settings file:

   ```bash
   python main_pipeline.py --config config/settings.yaml
   ```

   If you omit `--config`, the script falls back to the default configuration
   bundled with the project.

During execution, the following outcomes are expected:

- **MySQL updates** – ETL tasks insert or update rows in the
  `competitor_intel` schema. Check the `pipeline_runs` table to confirm success.
- **Excel reports** – Generated workbooks land in `reports/` (override via
  `config/settings.yaml`). Each file is timestamped and segmented by company or
  topic.
- **Summaries** – Narrative digests appear in `output/summaries/` as Markdown or
  plain-text files. These are also published to the database if summary storage
  is enabled.

### Scheduling

To run the pipeline on a schedule:

- **Cron** – Add an entry to your crontab, ensuring that the virtual environment
  and environment variables are loaded:

  ```cron
  0 6 * * * cd /path/to/Xspider && source .venv/bin/activate && python main_pipeline.py
  ```

- **Task schedulers** – For containerized deployments, configure Kubernetes
  CronJobs, Airflow DAGs, or similar orchestrators to execute the same command.
  Provide persistent volumes for `reports/` and `output/summaries/` so that
  generated artifacts are retained.

Monitor logs (stdout or the configured log file) for errors. Consider enabling an
external monitoring service or alert integration if daily execution is critical.

## Running Unit Tests

Unit tests live under the `tests/` directory and are written with `pytest`.
After installing dependencies, execute the test suite from the project root:

```bash
pytest tests/
```

For faster feedback during development, you can run specific tests or leverage
`pytest -k <expression>` to target subsets. Enable verbose output with `pytest -vv`
and generate coverage reports with `pytest --cov` if `pytest-cov` is installed.

---

If you encounter setup issues, verify that `.env`, YAML configs, and the MySQL
schema are in place before debugging application code.
