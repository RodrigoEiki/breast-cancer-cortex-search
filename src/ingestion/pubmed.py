import json
import os
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlencode

from src.common.http import fetch
from src.common.utils import stable_id
from src.processing.text import normalize_whitespace


def text_from_node(node) -> str:
    if node is None:
        return ""
    return normalize_whitespace("".join(node.itertext()))


def node_text(parent, path: str) -> str:
    return text_from_node(parent.find(path))


def article_date(article) -> str:
    pub_date = article.find(".//JournalIssue/PubDate")
    if pub_date is None:
        return ""
    year = node_text(pub_date, "Year")
    month = node_text(pub_date, "Month")
    day = node_text(pub_date, "Day")
    medline_date = node_text(pub_date, "MedlineDate")
    return normalize_whitespace(" ".join(part for part in [year, month, day] if part) or medline_date)


def article_doi(article) -> str:
    for article_id in article.findall(".//ArticleId"):
        if article_id.attrib.get("IdType") == "doi":
            return normalize_whitespace(article_id.text or "")
    for elocation in article.findall(".//ELocationID"):
        if elocation.attrib.get("EIdType") == "doi":
            return normalize_whitespace(elocation.text or "")
    return ""


def article_authors(article, limit: int = 12) -> str:
    names = []
    for author in article.findall(".//AuthorList/Author"):
        collective = node_text(author, "CollectiveName")
        if collective:
            names.append(collective)
            continue
        last = node_text(author, "LastName")
        initials = node_text(author, "Initials")
        if last:
            names.append(" ".join(part for part in [last, initials] if part))
    suffix = " et al." if len(names) > limit else ""
    return ", ".join(names[:limit]) + suffix


def article_abstract(article) -> str:
    parts = []
    for abstract_text in article.findall(".//Abstract/AbstractText"):
        label = abstract_text.attrib.get("Label")
        text = text_from_node(abstract_text)
        if text and label:
            parts.append(f"{label}: {text}")
        elif text:
            parts.append(text)
    return "\n\n".join(parts)


def pubmed_article_to_document(source: Dict, article, fetched_at: str) -> Dict:
    pmid = node_text(article, ".//MedlineCitation/PMID")
    title = node_text(article, ".//Article/ArticleTitle")
    journal = node_text(article, ".//Journal/Title")
    publication_date = article_date(article)
    doi = article_doi(article)
    authors = article_authors(article)
    abstract = article_abstract(article)
    publication_types = [
        text_from_node(node)
        for node in article.findall(".//PublicationTypeList/PublicationType")
        if text_from_node(node)
    ]
    mesh_terms = [
        text_from_node(node.find("DescriptorName"))
        for node in article.findall(".//MeshHeadingList/MeshHeading")
        if text_from_node(node.find("DescriptorName"))
    ]
    source_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "https://pubmed.ncbi.nlm.nih.gov/"
    content = "\n\n".join(
        part
        for part in [
            f"PMID: {pmid}",
            f"Title: {title}",
            f"Journal: {journal}",
            f"Publication date: {publication_date}",
            f"Authors: {authors}",
            f"Publication types: {', '.join(publication_types)}",
            f"MeSH terms: {', '.join(mesh_terms[:25])}",
            f"DOI: {doi}",
            f"Abstract: {abstract}",
        ]
        if part and not part.endswith(": ")
    )
    return {
        "document_id": stable_id(source_url),
        "source_name": source["source_name"],
        "source_tier": source["source_tier"],
        "source_url": source_url,
        "document_type": source["document_type"],
        "audience": source["audience"],
        "topic": source["topic"],
        "jurisdiction": source["jurisdiction"],
        "title": title or pmid,
        "pmid": pmid,
        "doi": doi,
        "journal": journal,
        "publication_date": publication_date,
        "publication_types": ", ".join(publication_types),
        "fetched_at": fetched_at,
        "content": normalize_whitespace(content),
    }


def pubmed_params(source: Dict, extra: Dict) -> Dict:
    params = {"tool": source.get("tool", "breast_cancer_cortex_search")}
    api_key = os.environ.get("NCBI_API_KEY") or source.get("api_key")
    if api_key:
        params["api_key"] = api_key
    params.update(extra)
    return params


def scrape_pubmed(config: Dict, fetched_at: str, raw_dir: Path) -> List[Dict]:
    source = config["pubmed"]
    esearch_params = pubmed_params(
        source,
        {
            "db": "pubmed",
            "term": source["query"],
            "retmax": str(source["max_results"]),
            "retmode": "json",
            "sort": source["sort"],
        },
    )
    esearch_url = f"{source['base_url']}/esearch.fcgi?{urlencode(esearch_params)}"
    esearch_body = fetch(esearch_url)
    (raw_dir / "pubmed_esearch.json").write_bytes(esearch_body)
    payload = json.loads(esearch_body.decode("utf-8"))
    ids = payload.get("esearchresult", {}).get("idlist", [])

    documents = []
    for offset in range(0, len(ids), source["batch_size"]):
        batch = ids[offset : offset + source["batch_size"]]
        efetch_params = pubmed_params(
            source,
            {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"},
        )
        efetch_url = f"{source['base_url']}/efetch.fcgi?{urlencode(efetch_params)}"
        body = fetch(efetch_url)
        batch_number = offset // source["batch_size"] + 1
        (raw_dir / f"pubmed_efetch_batch_{batch_number}.xml").write_bytes(body)
        root = ET.fromstring(body)
        for article in root.findall(".//PubmedArticle"):
            document = pubmed_article_to_document(source, article, fetched_at)
            if document["pmid"] and len(document["content"]) >= 120:
                documents.append(document)
        time.sleep(0.5)

    return documents
