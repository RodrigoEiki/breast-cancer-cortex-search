import json
from pathlib import Path
from typing import Any, Dict, Optional

from src.common.paths import CONFIG_PATH


def load_sources_config(path: Optional[Path] = None) -> Dict[str, Any]:
    config_path = path or CONFIG_PATH
    return json.loads(config_path.read_text(encoding="utf-8"))
