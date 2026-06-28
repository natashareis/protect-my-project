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

# Directories to never descend into during a full-repo scan.
# Built from patterns.py "dir" entries plus extras that have no gitignore suggestion.
_SKIP_DIRS: frozenset[str] = frozenset(
    {p["value"] for p in DEFAULT_IGNORE_PATTERNS if p.get("type") == "dir"}
    | {
        ".git",
        # Python venv variants
        "venv", "env", ".env",
        # Misc tooling caches
        ".tox", ".mypy_cache", ".ruff_cache", ".hypothesis",
        # Rust: target already in patterns; extra Go cache
        ".gomodcache",
        # Ruby: gems outside vendor
        ".gem",
        # General
        "bin",  # compiled outputs (Go, Rust CLI, .NET)
    }
)

# File suffixes that are always skipped (binary, compiled, lock, minified, media).
# Built from patterns.py "suffix" entries plus file types that are never source.
_SKIP_SUFFIXES: frozenset[str] = frozenset(
    {p["value"] for p in DEFAULT_IGNORE_PATTERNS if p.get("type") == "suffix"}
    | {
        # Lock files with a recognisable suffix
        ".lock",
        # Source maps already in patterns.py (.map)
        # Minified already in patterns.py (.min.js / .min.css)
        # Images
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".bmp", ".tiff", ".avif",
        # Fonts
        ".svg", ".woff", ".woff2", ".ttf", ".eot", ".otf",
        # Documents / archives
        ".pdf", ".zip", ".gz", ".tar", ".bz2", ".xz", ".7z", ".rar",
        # Database / binary blobs
        ".bin", ".dll", ".so", ".dylib", ".o", ".a", ".db", ".sqlite", ".sqlite3",
        # Media
        ".mp3", ".mp4", ".wav", ".ogg", ".flac", ".avi", ".mkv", ".mov",
        # Terraform state (can be large, contains infra metadata not inline secrets)
        ".tfstate",
    }
)

# Files with these exact names are skipped — lock / checksum files whose
# extension doesn't uniquely identify them.
_SKIP_NAMES: frozenset[str] = frozenset({
    # Node
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    # Python
    "poetry.lock",
    "Pipfile.lock",
    # PHP
    "composer.lock",
    # Ruby
    "Gemfile.lock",
    # Go
    "go.sum",
    # Rust
    "Cargo.lock",
    # Elixir
    "mix.lock",
    # Dart / Flutter
    "pubspec.lock",
    # .NET
    "packages.lock.json",
    # Chef
    "Berksfile.lock",
})

# Maximum file size to scan (512 KB); larger files are skipped
_MAX_FILE_BYTES: int = 512 * 1024

# Maximum snippet length stored in a Finding
_MAX_SNIPPET: int = 200


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
        stripped = line.strip()[:_MAX_SNIPPET]
        if PEM_HEADER.search(line):
            findings.append(Finding(path, i, stripped, "pem", "PEM private key header"))
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(path, i, stripped, "secret", name))
        # base64 check for long tokens
        tokens = re.findall(r"[A-Za-z0-9+/=]{32,}", line)
        for tok in tokens:
            if looks_like_base64(tok):
                findings.append(Finding(path, i, tok[:80], "secret", "base64-like"))
    return findings
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
    """Return list of scannable files under root.

    Skips:
    - build/dependency directories (node_modules, __pycache__, .venv, dist, …)
    - binary, compiled, lock, and minified file types
    - files larger than _MAX_FILE_BYTES
    """
    files: List[Path] = []

    def _walk(directory: Path) -> None:
        try:
            entries = list(directory.iterdir())
        except PermissionError:
            return
        for entry in entries:
            if entry.is_dir():
                if entry.name not in _SKIP_DIRS:
                    _walk(entry)
            elif entry.is_file():
                if entry.name in _SKIP_NAMES:
                    continue
                # Check every suffix component so ".min.js" is caught via ".js" check too
                if any(entry.name.endswith(s) for s in _SKIP_SUFFIXES):
                    continue
                try:
                    if entry.stat().st_size > _MAX_FILE_BYTES:
                        continue
                except OSError:
                    continue
                files.append(entry)

    _walk(root)
    return files
