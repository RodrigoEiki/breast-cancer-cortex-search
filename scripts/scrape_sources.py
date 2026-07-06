#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common.paths import PROCESSED_DIR, RAW_DIR
from src.ingestion.pipeline import run_ingestion


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-clinical-trials", action="store_true")
    parser.add_argument("--skip-pubmed", action="store_true")
    args = parser.parse_args()

    doc_count = run_ingestion(
        skip_clinical_trials=args.skip_clinical_trials,
        skip_pubmed=args.skip_pubmed,
    )

    print(f"Wrote {doc_count} documents")
    print(f"Raw output: {RAW_DIR}")
    print(f"Processed output: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
