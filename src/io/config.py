# src/io/config.py
from pathlib import Path
import yaml

from dotenv import load_dotenv
load_dotenv()

_CFG = None  # module-level cache


def load_config(path: str = "config/v1/weights.yaml"):
    """
    Lazy-load and cache the SR weights/knees config.
    """
    global _CFG
    if _CFG is None:
        text = Path(path).read_text(encoding="utf-8")
        _CFG = yaml.safe_load(text)
        if not isinstance(_CFG, dict):
            raise ValueError("Config must be a YAML mapping at the top level.")
    return _CFG
