# AGENTS.md

# Breast Cancer Cortex Search

## Project Overview

This repository demonstrates a production-oriented Retrieval-Augmented Generation (RAG) application built on Snowflake using Cortex Search.

The project showcases modern Snowflake AI capabilities, including:

- Snowflake Cortex Search
- Snowflake Cortex AI_COMPLETE
- Snowpark for Python
- Streamlit in Snowflake
- Python-based ingestion pipelines
- Snowflake-native text chunking

This project is intended for portfolio and client demonstration purposes. Prioritize clean architecture, maintainability, and production-quality code over quick implementations.

---

# Project Goals

The repository should demonstrate:

- Modular Python architecture
- Clean separation of concerns
- Production-style Snowflake deployment
- Reproducible ingestion pipelines
- High-quality code organization
- Extensible data ingestion
- Snowflake best practices

---

# Architecture

The application follows the pipeline below:

```text
Medical Sources
        │
        ▼
Python Ingestion
        │
        ▼
Normalization
        │
        ▼
JSONL Generation
        │
        ▼
Snowflake Stage
        │
        ▼
Raw Documents
        │
        ▼
SPLIT_TEXT_RECURSIVE_CHARACTER()
        │
        ▼
Chunk Table
        │
        ▼
Cortex Search
        │
        ▼
Streamlit
        │
        ▼
Cortex AI_COMPLETE
```

Avoid introducing unnecessary processing stages.

---

# Repository Structure

```text
app/
    Streamlit application

src/
    ingestion/
    processing/
    snowflake/
    common/

sql/
    Snowflake deployment scripts

configs/
    Configuration files

artifacts/
    Generated artifacts

docs/
    Documentation

tests/
    Unit tests
```

Each directory should have a single responsibility.

---

# Responsibilities

## app/

Contains only the user interface.

Responsibilities:

- User interaction
- Display results
- Invoke search services

Business logic should not live here.

## src/ingestion/

Responsible for:

- Downloading documents
- Calling APIs
- Scraping web pages
- Parsing source-specific formats
- Orchestrating ingestion

Each source should be isolated into its own module.

## src/processing/

Responsible for:

- Cleaning text
- Normalizing documents
- Metadata extraction
- Validation
- JSONL generation

Processing should remain independent from Snowflake.

## src/snowflake/

Contains only Snowflake-specific functionality.

Examples:

- Upload artifacts
- Execute SQL
- Query Cortex Search
- Snowpark helpers

Avoid mixing Snowflake code with ingestion logic.

## src/common/

Contains shared utilities.

Examples:

- Configuration
- Logging
- Shared helper functions
- Constants

---

# Data Sources

Current supported sources:

- National Cancer Institute (NCI)
- USPSTF
- SEER
- ClinicalTrials.gov
- PubMed (NCBI)

Future sources should follow the same ingestion interface.

Do not scrape:

- NCCN Guidelines
- Proprietary medical databases
- Copyrighted PDF content requiring authentication

---

# Document Model

Normalized documents should contain:

- id
- title
- content
- source
- url
- document_type
- last_updated
- metadata

All sources should produce the same schema.

Avoid source-specific output formats.

---

# Chunking Strategy

Production chunking must occur inside Snowflake using:

```sql
SPLIT_TEXT_RECURSIVE_CHARACTER()
```

Python should generate complete normalized documents only.

---

# Snowflake Responsibilities

Snowflake is responsible for:

- Document storage
- Text chunking
- Cortex Search indexing
- Semantic retrieval
- AI_COMPLETE generation

Avoid duplicating these capabilities in Python.

---

# Python Responsibilities

Python is responsible for:

- Data acquisition
- Parsing
- Cleaning
- Metadata extraction
- Validation
- JSONL generation

Python should not:

- Generate embeddings
- Perform semantic retrieval
- Perform production chunking

---

# SQL Guidelines

- SQL files should be idempotent.
- Use descriptive names.
- Number scripts in execution order.
- Prefer `CREATE OR REPLACE`.
- Prefer CTEs for readability.
- Avoid embedding large SQL statements inside Python.

---

# Streamlit Guidelines

Keep the application thin.

Responsibilities:

- Receive user questions
- Query Cortex Search
- Display retrieved context
- Invoke AI_COMPLETE
- Render citations

Do not implement ingestion or transformation logic inside the UI.

---

# Coding Standards

Prefer:

- Python 3.11+
- Type hints
- Dataclasses or Pydantic models
- Small reusable functions
- Composition over inheritance

Avoid:

- Global mutable state
- Hardcoded configuration
- Duplicate logic
- Monolithic scripts

---

# Error Handling

External requests should:

- Retry transient failures
- Log meaningful errors
- Continue processing remaining sources when possible

---

# Testing

Include unit tests whenever practical for:

- Parsing
- Normalization
- Validation
- Metadata extraction
- JSONL generation

---

# AI Coding Guidelines

When generating code:

- Prefer modifying existing modules over creating new ones.
- Reuse utilities before introducing duplicate functionality.
- Keep functions focused and reasonably small.
- Follow the existing repository structure.
- Keep business logic separate from infrastructure code.
- Use Snowflake-native capabilities whenever appropriate.
- Prefer maintainable solutions over clever ones.

---

# Primary Objective

Every change should reinforce:

- Production-ready architecture
- Clean code
- Maintainability
- Extensibility
- Reproducibility
- Snowflake best practices
- Portfolio-quality implementation
