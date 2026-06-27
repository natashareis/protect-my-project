#!/usr/bin/env python3
"""Run scanner directly (no subprocess) and output JSON results.

Usage:
    python scripts/run_scan_direct.py --target PATH
    # By default prints JSON to stdout; use `--out` to write to a file
"""
import argparse
import json
from pathlib import Path
from pmpp.scanner import list_repo_files, scan_paths, suggest_gitignore_for_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--out", default=None, help="If provided, write JSON report to this file; otherwise print to stdout")
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

    out_path = args.out
    if out_path:
        Path(out_path).write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")
        print(f"Wrote {out_path} (findings={len(findings)})")
    else:
        print(json.dumps(data, default=str, indent=2))


if __name__ == "__main__":
    main()
