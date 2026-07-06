-- Step 03: Load staged JSONL into RAW_DOCUMENTS.
-- Prerequisite: artifacts/processed/documents.jsonl is uploaded to
-- @BREAST_CANCER_SEARCH.RAG.BREAST_CANCER_STAGE.

TRUNCATE TABLE BREAST_CANCER_SEARCH.RAG.RAW_DOCUMENTS;

COPY INTO BREAST_CANCER_SEARCH.RAG.RAW_DOCUMENTS (
  DOCUMENT_ID,
  SOURCE_NAME,
  SOURCE_TIER,
  SOURCE_URL,
  DOCUMENT_TYPE,
  AUDIENCE,
  TOPIC,
  JURISDICTION,
  TITLE,
  NCT_ID,
  TRIAL_STATUS,
  TRIAL_PHASE,
  CONDITIONS,
  COUNTRIES,
  PMID,
  DOI,
  JOURNAL,
  PUBLICATION_DATE,
  PUBLICATION_TYPES,
  FETCHED_AT,
  CONTENT,
  RAW
)
FROM (
  SELECT
    $1:document_id::STRING,
    $1:source_name::STRING,
    $1:source_tier::NUMBER,
    $1:source_url::STRING,
    $1:document_type::STRING,
    $1:audience::STRING,
    $1:topic::STRING,
    $1:jurisdiction::STRING,
    $1:title::STRING,
    $1:nct_id::STRING,
    $1:trial_status::STRING,
    $1:trial_phase::STRING,
    $1:conditions::STRING,
    $1:countries::STRING,
    $1:pmid::STRING,
    $1:doi::STRING,
    $1:journal::STRING,
    $1:publication_date::STRING,
    $1:publication_types::STRING,
    $1:fetched_at::TIMESTAMP_TZ,
    $1:content::STRING,
    $1
  FROM @BREAST_CANCER_SEARCH.RAG.BREAST_CANCER_STAGE
);

SELECT
  'RAW_DOCUMENTS_LOADED' AS CHECK_NAME,
  COUNT(*) AS ROW_COUNT
FROM BREAST_CANCER_SEARCH.RAG.RAW_DOCUMENTS;

