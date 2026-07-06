import json
from typing import Any, Dict, List, Optional


DB_NAME = "BREAST_CANCER_SEARCH"
SCHEMA_NAME = "RAG"
SERVICE_NAME = "BREAST_CANCER_CORTEX_SEARCH"

SEARCH_COLUMNS = [
    "CHUNK_ID",
    "DOCUMENT_ID",
    "CONTENT",
    "SOURCE_NAME",
    "SOURCE_URL",
    "TITLE",
    "DOCUMENT_TYPE",
    "TOPIC",
    "SOURCE_TIER",
    "PMID",
    "NCT_ID",
    "TRIAL_STATUS",
    "PUBLICATION_DATE",
]


def build_filter(
    document_types: List[str],
    topics: List[str],
    source_tiers: List[int],
) -> Optional[Dict[str, Any]]:
    clauses: List[Dict[str, Any]] = []
    if document_types:
        clauses.append({"@or": [{"@eq": {"DOCUMENT_TYPE": value}} for value in document_types]})
    if topics:
        clauses.append({"@or": [{"@eq": {"TOPIC": value}} for value in topics]})
    if source_tiers:
        clauses.append({"@or": [{"@eq": {"SOURCE_TIER": value}} for value in source_tiers]})

    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"@and": clauses}


def search_with_python_api(
    session,
    query: str,
    result_limit: int,
    filters: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    from snowflake.core import Root

    root = Root(session)
    service = (
        root.databases[DB_NAME]
        .schemas[SCHEMA_NAME]
        .cortex_search_services[SERVICE_NAME]
    )
    response = service.search(
        query=query,
        columns=SEARCH_COLUMNS,
        filter=filters,
        limit=result_limit,
    )
    return json.loads(response.to_json()).get("results", [])


def search_with_sql_preview(
    session,
    query: str,
    result_limit: int,
    filters: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    payload: Dict[str, Any] = {
        "query": query,
        "columns": SEARCH_COLUMNS,
        "limit": result_limit,
    }
    if filters:
        payload["filter"] = filters

    payload_sql = json.dumps(payload).replace("\\", "\\\\").replace("'", "''")
    rows = session.sql(
        f"""
        SELECT PARSE_JSON(
          SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            '{DB_NAME}.{SCHEMA_NAME}.{SERVICE_NAME}',
            '{payload_sql}'
          )
        )['results'] AS RESULTS
        """
    ).collect()
    if not rows:
        return []
    results = rows[0]["RESULTS"]
    if results is None:
        return []
    if isinstance(results, str):
        return json.loads(results)
    return list(results)


def search_context(
    session,
    query: str,
    result_limit: int,
    filters: Optional[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], Optional[str]]:
    try:
        return search_with_python_api(session, query, result_limit, filters), None
    except Exception as exc:
        return search_with_sql_preview(session, query, result_limit, filters), str(exc)


def source_label(result: Dict[str, Any], index: int) -> str:
    source_name = result.get("SOURCE_NAME") or "Source"
    title = result.get("TITLE") or source_name
    pmid = result.get("PMID")
    nct_id = result.get("NCT_ID")
    if pmid:
        return f"[{index}] {title} | PMID {pmid}"
    if nct_id:
        status = result.get("TRIAL_STATUS")
        return f"[{index}] {title} | {nct_id}" + (f" ({status})" if status else "")
    return f"[{index}] {title}"


def build_context(results: List[Dict[str, Any]]) -> str:
    blocks = []
    for index, result in enumerate(results, start=1):
        metadata = [
            f"source_name={result.get('SOURCE_NAME', '')}",
            f"document_type={result.get('DOCUMENT_TYPE', '')}",
            f"topic={result.get('TOPIC', '')}",
            f"url={result.get('SOURCE_URL', '')}",
            f"pmid={result.get('PMID', '')}",
            f"nct_id={result.get('NCT_ID', '')}",
            f"trial_status={result.get('TRIAL_STATUS', '')}",
            f"publication_date={result.get('PUBLICATION_DATE', '')}",
        ]
        blocks.append(
            "\n".join(
                [
                    f"Source [{index}]: {result.get('TITLE') or result.get('SOURCE_NAME')}",
                    "; ".join(metadata),
                    result.get("CONTENT", ""),
                ]
            )
        )
    return "\n\n---\n\n".join(blocks)


def build_prompt(question: str, results: List[Dict[str, Any]]) -> str:
    context = build_context(results)
    return f"""
You are a research and clinical evidence assistant for breast cancer literature and guidance.

Use only the retrieved context below. If the retrieved context is insufficient, say what is missing.
Do not provide diagnosis or treatment instructions for an individual patient.
Distinguish clearly between clinical guidelines, screening recommendations, statistics, clinical trials, and research abstracts.
Cite sources inline using bracketed numbers like [1] and include uncertainty where evidence is preliminary.

Retrieved context:
{context}

User question:
{question}

Answer:
""".strip()


def generate_answer(session, model: str, question: str, results: List[Dict[str, Any]]) -> str:
    prompt = build_prompt(question, results)
    escaped_model = model.replace("'", "''")
    escaped_prompt = prompt.replace("\\", "\\\\").replace("'", "''")
    rows = session.sql(
        f"""
        SELECT SNOWFLAKE.CORTEX.AI_COMPLETE(
          model => '{escaped_model}',
          prompt => '{escaped_prompt}',
          model_parameters => OBJECT_CONSTRUCT('temperature', 0, 'max_tokens', 1600),
          show_details => TRUE
        ) AS RESPONSE
        """
    ).collect()
    if not rows or rows[0]["RESPONSE"] is None:
        return "I could not generate an answer from the retrieved context."

    response = rows[0]["RESPONSE"]
    if isinstance(response, str):
        try:
            payload = json.loads(response)
            if isinstance(payload, dict):
                choices = payload.get("choices") or []
                if choices and isinstance(choices[0], dict):
                    return choices[0].get("messages") or response
                return payload.get("response") or response
        except json.JSONDecodeError:
            return response
    if isinstance(response, dict):
        choices = response.get("choices") or []
        if choices and isinstance(choices[0], dict):
            return choices[0].get("messages") or json.dumps(response, indent=2)
        return response.get("response") or json.dumps(response, indent=2)
    return str(response)

