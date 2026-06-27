"""Git and filesystem utility helpers."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from pmpp.scanner import list_repo_files


def get_changed_files(root: Path) -> List[Path]:
    """Get changed/unstaged files via git; fallback to all files.

    Returns a list of Path objects under root.
    """
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True)
        files = []
        for line in out.splitlines():
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                files.append(root / parts[1])
        return files
    except Exception:
        return list_repo_files(root)
