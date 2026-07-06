# 🩺 Breast Cancer Cortex Search

Breast Cancer Cortex Search is a portfolio project demonstrating how to
build a production-oriented Retrieval-Augmented Generation application
using Snowflake Cortex Search, Snowflake-native text chunking, Cortex
`AI_COMPLETE`, and Streamlit in Snowflake.

The application retrieves breast cancer guidance, statistics, clinical
trial records, and research abstracts from normalized source documents.
Snowflake performs document storage, chunking, semantic retrieval, and
answer generation, while Python handles acquisition, parsing,
normalization, validation, and JSONL artifact generation.

------------------------------------------------------------------------

## 🎬 Demo

> Demo GIF placeholder

```md
![Breast Cancer Cortex Search Demo](docs/assets/demo.gif)
```

------------------------------------------------------------------------

## 🏗️ Architecture

> Architecture diagram placeholder

```md
![Architecture](docs/assets/architecture.png)
```

```text
Medical Sources
        |
        v
Python Ingestion
        |
        v
Normalization
        |
        v
JSONL Generation
        |
        v
Snowflake Stage
        |
        v
Raw Documents
        |
        v
SPLIT_TEXT_RECURSIVE_CHARACTER()
        |
        v
Chunk Table
        |
        v
Cortex Search
        |
        v
Streamlit in Snowflake
        |
        v
Cortex AI_COMPLETE
```

------------------------------------------------------------------------

## ✨ Key Features

- 🔎 Evidence search over normalized breast cancer documents
- ❄️ Snowflake-native chunking with `SPLIT_TEXT_RECURSIVE_CHARACTER()`
- 🧠 Semantic retrieval with Cortex Search
- 💬 Cited answer generation with Cortex `AI_COMPLETE`
- 🐍 Source-specific Python ingestion for public medical data
- 🎈 Thin Streamlit interface designed for Streamlit in Snowflake
- 🗄️ Idempotent SQL deployment scripts
- ✅ Offline unit tests for ingestion, processing, and Snowflake helpers

------------------------------------------------------------------------

## 📁 Repository Structure

```text
app/        Streamlit application
src/        Python ingestion, processing, Snowflake, and shared utilities
sql/        Snowflake deployment and validation scripts
configs/    Source configuration
artifacts/  Generated raw and processed artifacts
docs/       Architecture, data source, and deployment notes
tests/      Unit tests
scripts/    Local artifact generation entrypoints
```

------------------------------------------------------------------------

## 🛠️ Technology Stack

| Category | Technologies |
| --- | --- |
| 🐍 Language | Python 3.11+ |
| ❄️ Data Warehouse | Snowflake |
| 🤖 AI | Cortex Search, Cortex `AI_COMPLETE` |
| 🎈 Framework | Streamlit in Snowflake |
| ⚙️ Data Processing | Snowpark for Python, Python standard library |
| 📦 Storage Format | JSONL |
| ✅ Testing | unittest |

------------------------------------------------------------------------

## 🗂️ Data Sources

Current supported public sources include:

- National Cancer Institute breast cancer pages and PDQ summaries
- USPSTF breast cancer screening recommendation
- SEER female breast cancer statistics
- ClinicalTrials.gov breast cancer study records
- PubMed breast cancer research abstracts through NCBI E-utilities

Source definitions live in:

```text
configs/sources.json
```

NCCN Guidelines, proprietary medical databases, and authenticated
copyrighted PDF content are intentionally excluded.

------------------------------------------------------------------------

## 📦 Artifact Generation

Run the ingestion pipeline locally:

```bash
python3 scripts/scrape_sources.py
```

The canonical Snowflake load artifact is:

```text
artifacts/processed/documents.jsonl
```

Generated artifacts are organized as:

```text
artifacts/raw/                  Raw HTML, JSON, and XML responses
artifacts/processed/documents.jsonl
```

Python writes complete normalized documents only. Production chunking is
performed in Snowflake.

------------------------------------------------------------------------

## 🚀 Deployment

This project is designed to run inside Snowflake using Streamlit in
Snowflake. The Snowflake-native app entrypoint is:

```text
app/streamlit_app.py
```

The Streamlit package environment is defined in:

```text
app/environment.yml
```

The Streamlit app is not a standalone file. It imports shared Cortex
Search and `AI_COMPLETE` helpers from `src/`, so deploy the application
with both of these paths available:

```text
app/streamlit_app.py
src/
```

The deployment flow is:

1. Generate `artifacts/processed/documents.jsonl` with the Python
   ingestion pipeline.
2. Run `sql/01_create_database_schema.sql`.
3. Upload `artifacts/processed/documents.jsonl` to the Snowflake stage:

```text
@BREAST_CANCER_SEARCH.RAG.BREAST_CANCER_STAGE
```

4. Run the remaining SQL scripts in order:

```sql
sql/02_create_raw_documents_table.sql
sql/03_load_raw_documents.sql
sql/04_create_document_chunks.sql
sql/05_create_cortex_search_service.sql
sql/06_validate_app_dependencies.sql
```

5. Deploy `app/streamlit_app.py` as the Streamlit in Snowflake app,
   including the `src/` package with the app files.

The app queries:

```text
BREAST_CANCER_SEARCH.RAG.BREAST_CANCER_CORTEX_SEARCH
```

Full deployment notes are available in `docs/deployment.md`.

------------------------------------------------------------------------

## ✅ Tests

Run the offline unit test suite:

```bash
python3 -m unittest discover tests
```

------------------------------------------------------------------------

## 🔮 Future Improvements

- 💬 Chat history
- ⚡ Query result caching
- 🔁 Multi-turn question answering
- 🧩 Additional source connectors
- 🕒 Automated source freshness checks
- ✅ CI validation for generated JSONL artifacts
- 🚀 Deployment automation with Snowflake CLI

------------------------------------------------------------------------

## 📌 About

This project showcases production-style RAG architecture with Snowflake,
Cortex Search, Snowflake-native chunking, Python ingestion pipelines, and
Streamlit application development.
