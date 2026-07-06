import json
import time
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlencode

from src.common.http import fetch
from src.common.utils import stable_id
from src.processing.text import normalize_whitespace


def trial_to_document(source: Dict, study: Dict, fetched_at: str) -> Dict:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    conditions = protocol.get("conditionsModule", {})
    arms = protocol.get("armsInterventionsModule", {})
    eligibility = protocol.get("eligibilityModule", {})
    contacts = protocol.get("contactsLocationsModule", {})
    description = protocol.get("descriptionModule", {})
    locations = contacts.get("locations", [])
    countries = sorted(
        {location.get("country", "") for location in locations if location.get("country", "")}
    )
    location_preview = [
        ", ".join(
            value
            for value in [
                location.get("facility", ""),
                location.get("city", ""),
                location.get("state", ""),
                location.get("country", ""),
            ]
            if value
        )
        for location in locations[:10]
    ]
    phases = design.get("phases", [])
    conditions_list = conditions.get("conditions", [])
    interventions = [
        intervention.get("name", "")
        for intervention in arms.get("interventions", [])
        if intervention.get("name", "")
    ]

    nct_id = identification.get("nctId", "")
    title = identification.get("briefTitle") or identification.get("officialTitle") or nct_id
    url = f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else "https://clinicaltrials.gov/"

    content_parts = [
        f"Trial ID: {nct_id}",
        f"Title: {title}",
        f"Status: {status.get('overallStatus', '')}",
        f"Phases: {', '.join(phases)}",
        f"Study type: {design.get('studyType', '')}",
        f"Conditions: {', '.join(conditions_list)}",
        f"Brief summary: {description.get('briefSummary', '')}",
        f"Detailed description: {description.get('detailedDescription', '')}",
        f"Interventions: {', '.join(interventions)}",
        f"Eligibility: {eligibility.get('eligibilityCriteria', '')}",
        f"Sex: {eligibility.get('sex', '')}",
        f"Minimum age: {eligibility.get('minimumAge', '')}",
        f"Maximum age: {eligibility.get('maximumAge', '')}",
        f"Location count: {len(locations)}",
        f"Countries: {', '.join(countries)}",
        f"Representative locations: {'; '.join(location_preview)}",
    ]

    return {
        "document_id": stable_id(url),
        "source_name": source["source_name"],
        "source_tier": source["source_tier"],
        "source_url": url,
        "document_type": source["document_type"],
        "audience": source["audience"],
        "topic": source["topic"],
        "jurisdiction": source["jurisdiction"],
        "title": title,
        "nct_id": nct_id,
        "trial_status": status.get("overallStatus", ""),
        "trial_phase": ", ".join(phases),
        "conditions": ", ".join(conditions_list),
        "countries": ", ".join(countries),
        "fetched_at": fetched_at,
        "content": normalize_whitespace("\n\n".join(p for p in content_parts if p)),
    }


def is_breast_cancer_study(study: Dict) -> bool:
    protocol = study.get("protocolSection", {})
    conditions = protocol.get("conditionsModule", {}).get("conditions", [])
    identification = protocol.get("identificationModule", {})
    description = protocol.get("descriptionModule", {})
    haystack = " ".join(
        conditions
        + [
            identification.get("briefTitle", ""),
            identification.get("officialTitle", ""),
            description.get("briefSummary", ""),
        ]
    ).lower()
    return "breast" in haystack


def scrape_clinical_trials(config: Dict, fetched_at: str, raw_dir: Path) -> List[Dict]:
    source = config["clinical_trials"]
    documents = []
    page_token = None

    for page in range(source["max_pages"]):
        params = {
            "query.cond": source["condition"],
            "pageSize": str(source["page_size"]),
            "format": "json",
        }
        if page_token:
            params["pageToken"] = page_token

        url = f"{source['base_url']}?{urlencode(params)}"
        body = fetch(url)
        (raw_dir / f"clinicaltrials_breast_cancer_page_{page + 1}.json").write_bytes(body)
        payload = json.loads(body.decode("utf-8"))

        for study in payload.get("studies", []):
            if is_breast_cancer_study(study):
                documents.append(trial_to_document(source, study, fetched_at))

        page_token = payload.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.5)

    return documents

