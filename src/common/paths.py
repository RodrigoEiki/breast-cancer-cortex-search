from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sources.json"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
RAW_DIR = ARTIFACTS_DIR / "raw"
PROCESSED_DIR = ARTIFACTS_DIR / "processed"
