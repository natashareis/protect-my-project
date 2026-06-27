"""Core scanner heuristics and helpers.

Provides functions to scan files for likely secrets, suggest .gitignore entries,
and recommend environment variable extraction.
"""
from __future__ import annotations

import base64
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from pmpp.utils.patterns import DEFAULT_IGNORE_PATTERNS


@dataclass
class Finding:
    path: Path
    line_no: int
    snippet: str
    kind: str  # e.g., 'secret', 'pem', 'env_suggestion', 'gitignore'
    detail: Optional[str] = None


SECRET_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("OPENAI", re.compile(r"sk-[A-Za-z0-9\-]{20,}") ),
    ("AWS_AKIA", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GCP_API_KEY", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("GITHUB_TOKEN", re.compile(r"ghp_[0-9A-Za-z_]{36}")),
    ("GENERIC_KEY", re.compile(r"[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}")),
]

PEM_HEADER = re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----")


def shannon_entropy(data: bytes) -> float:
    """Compute approximate Shannon entropy of bytes."""
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0.0
    length = len(data)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def looks_like_base64(s: str) -> bool:
    try:
        b = s.encode("utf-8")
        # strip padding
        clean = s.strip().rstrip("=")
        if len(clean) == 0:
            return False
        # must be valid base64 charset
        if not re.fullmatch(r"[A-Za-z0-9+/=\n\r]+", s):
            return False
        decoded = base64.b64decode(s + "===", validate=False)
        ent = shannon_entropy(decoded)
        return ent > 3.5
    except Exception:
        return False


def find_secrets_in_text(path: Path, text: str) -> List[Finding]:
    """Return list of secret-like findings in text."""
    findings: List[Finding] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if PEM_HEADER.search(line):
            findings.append(Finding(path, i, line.strip(), "pem", "PEM private key header"))
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(path, i, line.strip(), "secret", name))
        # base64 check for long tokens
        tokens = re.findall(r"[A-Za-z0-9+/=]{32,}", line)
        for tok in tokens:
            if looks_like_base64(tok):
                findings.append(Finding(path, i, tok[:80], "secret", "base64-like"))
    return findings


def suggest_gitignore_for_path(path: Path) -> Optional[str]:
    """Suggest a .gitignore entry for the provided path."""
    # Check against default ignore patterns first
    name = path.name
    for p in DEFAULT_IGNORE_PATTERNS:
        t = p.get("type")
        val = p.get("value")
        sugg = p.get("suggest")
        if t == "dir" and name == val:
            return sugg
        if t == "suffix" and name.endswith(val):
            return sugg
        if t == "name" and name == val:
            return sugg
        if t == "path_contains" and val in path.as_posix():
            return sugg

    # fallback heuristics
    if path.is_dir():
        return f"{path.name}/"
    parts = path.parts
    if len(parts) >= 2 and parts[0] in ("build", "dist", "target"):
        return f"{parts[0]}/"
    # typical files
    if name in (".env", "credentials.json"):
        return name
    if name.endswith(('.pem', '.key', '.p12')):
        return name
    return None


def scan_paths(paths: Iterable[Path]) -> List[Finding]:
    """Scan given paths (files) and return list of findings."""
    findings: List[Finding] = []
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        findings.extend(find_secrets_in_text(p, text))
    return findings


def list_repo_files(root: Path) -> List[Path]:
    """Return list of files under root, excluding .git directory."""
    files: List[Path] = []
    for p in root.rglob("*"):
        if ".git" in p.parts:
            continue
        if p.is_file():
            files.append(p)
    return files
