from typing import Dict, List

from src.common.config import load_sources_config
from src.common.paths import PROCESSED_DIR, RAW_DIR
from src.common.utils import utc_now, write_jsonl
from src.ingestion.clinical_trials import scrape_clinical_trials
from src.ingestion.html_sources import scrape_html_sources
from src.ingestion.pubmed import scrape_pubmed


def collect_documents(
    config: Dict,
    skip_clinical_trials: bool = False,
    skip_pubmed: bool = False,
) -> List[Dict]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = utc_now()
    documents = scrape_html_sources(config, fetched_at, RAW_DIR)
    if not skip_clinical_trials:
        documents.extend(scrape_clinical_trials(config, fetched_at, RAW_DIR))
    if not skip_pubmed:
        documents.extend(scrape_pubmed(config, fetched_at, RAW_DIR))
    return documents


def run_ingestion(
    skip_clinical_trials: bool = False,
    skip_pubmed: bool = False,
) -> int:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    config = load_sources_config()
    documents = collect_documents(config, skip_clinical_trials, skip_pubmed)
    return write_jsonl(PROCESSED_DIR / "documents.jsonl", documents)
