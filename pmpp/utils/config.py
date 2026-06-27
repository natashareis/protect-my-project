"""Configuration loader for pmpp (utilities).

Supports a simple `.pmpp.toml` file at the repository root to override
defaults. Falls back to sensible defaults.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

try:
    import tomllib  # Python 3.11+
except Exception:
    import tomli as tomllib  # type: ignore


DEFAULT_CONFIG: Dict[str, Any] = {
    "ignore": {
        "enabled": ["node", "python", "java", "rust"],
    },
    "llm": {
        "provider": "none",  # 'none' or 'suggest'
        "budget": 1,
    },
}


def load_config(root: Path) -> Dict[str, Any]:
    cfg = DEFAULT_CONFIG.copy()
    p = root / ".pmpp.toml"
    if not p.exists():
        return cfg
    try:
        data = tomllib.loads(p.read_text(encoding="utf-8"))
        # shallow merge
        for k, v in data.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    except Exception:
        # ignore parse errors and return defaults
        return cfg
    return cfg
