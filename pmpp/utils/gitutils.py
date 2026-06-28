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
            if len(line) < 4:
                continue
            # porcelain format: XY<space><path>; XY is always 2 chars
            path_part = line[3:]
            # renamed files: "old -> new" — take only the new path
            if " -> " in path_part:
                path_part = path_part.split(" -> ")[-1]
            files.append(root / path_part)
        return files
    except Exception:
        return list_repo_files(root)
