# East Africa Economic Pulse (EAEP)

Automated data pipeline for East African economic indicators — ingestion, orchestration, star-schema storage, and API exposure built end-to-end on real World Bank data.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-star_schema-336791)
![Prefect](https://img.shields.io/badge/Prefect-2.16-024DFD)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688)
![Docker](https://img.shields.io/badge/Docker-containerized-2496ED)
![Status](https://img.shields.io/badge/status-live-brightgreen)

**Live demo:** <https://eaep-api.onrender.com>

---

## Why this project

World Bank, IMF and African Development Bank publish annual economic data for every country — but it's scattered across incompatible formats and inaccessible without processing. EAEP solves exactly that problem for 5 East African countries: **collect, clean, unify, store, expose.**

Built as a second portfolio project to demonstrate skills a single full-stack app (see [tontine-platform](https://github.com/Allianzj04/tontine-platform)) can't: working with real institutional data at scale, automating pipelines end-to-end, and using the standard Data Engineering toolchain rather than general backend tools.

## What it does

- Collects 4 economic indicators for 5 countries (2010–2023) from the World Bank API
- Cleans and reshapes the data (wide → long format) with Pandas and Polars
- Stores it in PostgreSQL as a proper analytical warehouse (star schema)
- Runs automatically on a schedule, orchestrated by Prefect — no manual execution
- Exposes the data through a documented FastAPI REST API
- Visualizes it through an interactive Chart.js dashboard

## Indicators covered

| Indicator | World Bank code | Coverage |
| --- | --- | --- |
| GDP per capita (current US$) | `NY.GDP.PCAP.CD` | 70/70, no nulls |
| Inflation, consumer prices (annual %) | `FP.CPI.TOTL.ZG` | 70/70, no nulls |
| Official exchange rate (LCU per US$) | `PA.NUS.FCRF` | 70/70, no nulls |
| Unemployment, ILO modeled estimate (%) | `SL.UEM.TOTL.ZS` | 70/70, no nulls |

**Countries:** Burundi, Kenya, Rwanda, Tanzania, Uganda — 2010 to 2023 (14 years each).

A 5th candidate indicator, central government debt (% of GDP, `GC.DOD.TOTL.GD.ZS`), was evaluated and **deliberately excluded**: 64 of 70 values were null (only Uganda, 2018–2023, had usable data), making it unusable for a 5-country comparison. Verifying real data coverage before committing to the pipeline is a deliberate step in this project, not an afterthought.

## Architecture

```mermaid
flowchart LR
    A[World Bank API<br/>wbgapi] -->|Pandas: reshape| B[ingestion/<br/>fetch_indicators.py]
    B -->|Polars: clean + transform| C[Prefect flow<br/>run_pipeline.py]
    C -->|scheduled monthly| D[(PostgreSQL<br/>star schema)]
    D --> E[FastAPI<br/>api/main.py]
    E --> F[Dashboard<br/>Chart.js]
    E --> G[Swagger docs<br/>/docs]
```

**Why a star schema and not a transactional schema:** `fact_economic` holds the numeric measurements (value, year), while `dim_country` and `dim_indicator` hold stable descriptive attributes. This separation is optimized for analytical queries (compare, rank, trend) rather than transactional updates — the same reason data warehouses in production use this pattern instead of a normalized relational schema.

```
dim_country (id, code, name)
dim_indicator (id, code, label)
fact_economic (id, country_id FK, indicator_id FK, year, value)
  UNIQUE(country_id, indicator_id, year)  -- idempotency guarantee
```

The `UNIQUE` constraint combined with `ON CONFLICT DO NOTHING` on every insert makes the pipeline **idempotent**: re-running it never creates duplicates, regardless of how many times it fires.

## Tech stack and why each tool was chosen

| Tool | Role | Why |
| --- | --- | --- |
| **Pandas** | Initial reshape (wide → long) | `wbgapi` returns Pandas natively — no way around it |
| **Polars** | All transformations after reshape | Faster than Pandas at scale; the tool Data Engineering teams are adopting now |
| **PostgreSQL** | Warehouse storage | Production-standard relational database, modeled as a star schema |
| **Prefect** | Orchestration + scheduling | Turns a script into a pipeline: automatic retries, logging, and a scheduler — simpler to adopt than Airflow |
| **FastAPI** | Data exposure | Async, typed, auto-documented via Swagger (`/docs`) |
| **Docker** | Containerizing the API | Portable: anyone can run the service with one command |
| **SQL window functions / CTEs** | Analytical queries | `LAG()`, `RANK()`, `WITH` — what Pandas doesn't replace; fundamental in Data Engineering |

## Analytical queries

Three SQL queries in `storage/queries.sql` answer real business questions, not just data extraction:

1. **13-year GDP growth rate per country** (`LAG(value, 13)` + CTE) — Kenya leads at +78%, Burundi lowest at +16%
2. **Country ranking by GDP per capita in a given year** (`RANK()`) — Kenya #1, Burundi #5 in 2023
3. **Year-over-year growth** (`LAG(value, 1)`) — tracks short-term swings, including currency-driven negative growth

## API endpoints

| Endpoint | Description |
| --- | --- |
| `GET /countries` | List of the 5 countries |
| `GET /gdp?page=1&limit=20` | Paginated indicator data |
| `GET /gdp/{country_code}?indicator=gdp_per_capita` | Time series for one country, filtered by indicator |
| `GET /countries/ranking?year=2023&indicator=gdp_per_capita` | Country ranking for a given year and indicator |
| `GET /docs` | Interactive Swagger documentation |

## Orchestration and scheduling

The pipeline runs as a Prefect **flow** (`run_pipeline.py`), composed of two **tasks** — ingestion and storage — each with automatic logging and failure capture.

```python
launch.serve(name='eaep-pipeline', cron='0 6 1 * *')  # 1st of every month, 6 AM
```

Since all 4 indicators are annual World Bank figures, a monthly schedule is sufficient — there is no value in polling more frequently; the underlying data simply doesn't change faster than that.

**Known limitation:** `.serve()` starts a long-running local process that polls for scheduled runs. The schedule only fires while that process is active — it is not yet deployed as an always-on service. Running it continuously in production (e.g. via a Render background worker) is a deliberate next step, not an oversight.

## Running locally

```bash
git clone https://github.com/Allianzj04/east-africa-economic-pulse.git
cd east-africa-economic-pulse
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost:5432/east_africa_pulse
```

Set up the database and populate it:

```bash
psql -U postgres -c "CREATE DATABASE east_africa_pulse"
psql -d east_africa_pulse -f storage/schema.sql
python -m storage.load
```

Run the API:

```bash
uvicorn api.main:app --reload
```

Dashboard available at `http://localhost:8000`, Swagger docs at `http://localhost:8000/docs`.

Run the orchestrated pipeline with scheduling:

```bash
python run_pipeline.py
```

## Running with Docker

```bash
docker build -t eaep-api .
docker run -p 8000:8000 --env-file .env eaep-api
```

> On Windows/Mac, use `-e DATABASE_URL=...` with `host.docker.internal` instead of `localhost` if connecting to a local PostgreSQL instance from inside the container.

## Deployment

Deployed on **Render**:

- `eaep-db` — managed PostgreSQL (populated via the External URL, consumed by the API via the Internal URL)
- `eaep-api` — Dockerized web service, built directly from the repo's `Dockerfile`

`DATABASE_URL` is parsed via `urllib.parse.urlparse()` and injected as an environment variable at runtime — never baked into the Docker image (`.env` is excluded via both `.gitignore` and `.dockerignore`, defense in depth).

## Dashboard

`<!-- TODO: add a screenshot of the dashboard here, e.g. ![Dashboard](docs/screenshot-dashboard.png) -->`

`<!-- TODO: add a screenshot of /docs (Swagger UI) here -->`

Built with vanilla JS and Chart.js — country and indicator selectors drive a single chart, re-rendered on change (`chart.destroy()` before each `new Chart()` to avoid canvas overlap).

## Known limitations and technical debt

- `get_connection()` is duplicated in `storage/load.py` and `api/database.py` — a DRY refactor into a shared `storage/db.py` is planned but non-blocking
- Prefect scheduling runs via a local long-lived process (see *Orchestration and scheduling* above); not yet deployed as an always-on worker
- No automated tests on the pipeline side yet (ingestion/storage); API has pytest coverage on core endpoints

## What this project demonstrates

A self-taught student building, from Burundi, a fully automated data pipeline on real institutional data — not toy exercises — covering the standard Data Engineering toolchain: ingestion, transformation at scale, orchestration, analytical SQL, containerization, and production deployment with a public URL.

Paired with [tontine-platform](https://github.com/Allianzj04/tontine-platform) (full-stack Django + FastAPI application), these two projects cover complementary ground: backend engineering and data engineering.

## Roadmap

- [ ] Deploy Prefect scheduling as an always-on service (Render background worker)
- [ ] Refactor duplicated database connection logic (DRY)
- [ ] Add automated tests for ingestion and storage modules
- [ ] Evaluate a 5th/6th indicator once Phase 5 documentation is complete

## Author

Allianzj04 — Software Engineering student, Burundi. Self-taught, targeting a Data / Backend program.
