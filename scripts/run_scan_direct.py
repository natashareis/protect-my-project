#!/usr/bin/env python3
"""Run scanner directly (no subprocess) and write JSON results.

Usage:
  python scripts/run_scan_direct.py --target PATH --out pmpp-results.json
"""
import argparse
import json
from pathlib import Path
from pmpp.scanner import list_repo_files, scan_paths, suggest_gitignore_for_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--out", default="pmpp-results.json")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    files = list_repo_files(root)
    findings = scan_paths(files)

    gitignore_suggestions = {}
    for f in findings:
        gi = suggest_gitignore_for_path(f.path)
        if gi:
            gitignore_suggestions[gi] = True

    data = {
        "findings": [f.__dict__ for f in findings],
        "gitignore": list(gitignore_suggestions.keys()),
        "summary": {
            "clean": len(findings) == 0,
            "message": ("No findings — the project appears to be clean. Human review is still recommended.")
        }
    }

    Path(args.out).write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")
    print(f"Wrote {args.out} (findings={len(findings)})")


if __name__ == "__main__":
    main()
