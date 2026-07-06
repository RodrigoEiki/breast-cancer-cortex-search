# Architecture

This project is a production-oriented Snowflake RAG demo for breast cancer evidence search.

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

Python acquires, parses, cleans, validates, and writes complete normalized documents. Snowflake stores documents, chunks text, indexes content with Cortex Search, retrieves context, and generates answers.

## Layout

- `app/`: Streamlit user interface only.
- `src/ingestion/`: source-specific acquisition and parsing.
- `src/processing/`: text extraction and normalization.
- `src/snowflake/`: Cortex Search and AI_COMPLETE helpers.
- `src/common/`: shared configuration, paths, HTTP, IDs, and JSONL writing.
- `configs/`: source definitions.
- `artifacts/`: generated raw and processed outputs.
- `sql/`: idempotent Snowflake deployment and validation scripts.
- `tests/`: offline unit tests.
