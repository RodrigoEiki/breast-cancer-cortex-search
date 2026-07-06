import time
from pathlib import Path
from typing import Dict, List

from src.common.http import fetch
from src.common.utils import safe_filename, stable_id
from src.processing.text import extract_html_text


def parse_html_document(source: Dict, body: bytes, fetched_at: str) -> Dict:
    text, title = extract_html_text(body)
    return {
        "document_id": stable_id(source["url"]),
        "source_name": source["source_name"],
        "source_tier": source["source_tier"],
        "source_url": source["url"],
        "document_type": source["document_type"],
        "audience": source["audience"],
        "topic": source["topic"],
        "jurisdiction": source["jurisdiction"],
        "title": title or source["source_name"],
        "fetched_at": fetched_at,
        "content": text,
    }


def scrape_html_sources(config: Dict, fetched_at: str, raw_dir: Path) -> List[Dict]:
    documents = []
    for source in config["html_sources"]:
        url = source["url"]
        body = fetch(url)
        (raw_dir / f"{safe_filename(url)}.html").write_bytes(body)
        documents.append(parse_html_document(source, body, fetched_at))
        time.sleep(0.5)
    return documents

