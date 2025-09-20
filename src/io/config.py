import os
import yaml
from pathlib import Path
from typing import Optional

_CFG = None
_CFG_PATH: Optional[Path] = None

def load_config(path: str = None, *, force: bool = False):
    """
    Load and cache SR config. Set SR_CONFIG_PATH to override default.
    Use force=True to bypass cache (for debugging/reloads).
    """
    global _CFG, _CFG_PATH
    if path is None:
        path = os.getenv("SR_CONFIG_PATH", "config/v1/weights.yaml")

    cfg_path = Path(path).resolve()

    if force or _CFG is None or _CFG_PATH != cfg_path:
        text = cfg_path.read_text(encoding="utf-8")
        _CFG = yaml.safe_load(text)
        _CFG_PATH = cfg_path
        # simple trace
        print(f"[dac-sr] loaded config: {_CFG_PATH}")

    return _CFG
