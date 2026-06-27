#!/usr/bin/env python3
"""Run scanner skipping common dependency folders to reduce noise."""
import argparse
import json
from pathlib import Path
from collections import Counter
import fnmatch
from pmpp.scanner import list_repo_files, scan_paths, suggest_gitignore_for_path


COMMON_EXCLUDE = {"node_modules", ".venv", "venv", "__pycache__"}
# also skip pmpp-generated report files to avoid scanning previous outputs
EXTRA_EXCLUDE_PATTERNS = ("pmpp-*.json", "pmpp-results-*.json", "pmpp_self_*.json", "pmpp-self-*.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--out", default=None, help="If provided, write JSON report to this file; otherwise print to stdout")
    parser.add_argument("--no-exclude", action="store_true", help="Do not exclude common dependency folders")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    files = list_repo_files(root)
    if not args.no_exclude:
        files = [
            p for p in files
            if not (
                set(p.parts) & COMMON_EXCLUDE
                or any(fnmatch.fnmatch(p.name, pat) for pat in EXTRA_EXCLUDE_PATTERNS)
            )
        ]

    findings = scan_paths(files)

    gitignore_suggestions = {}
    for f in findings:
        gi = suggest_gitignore_for_path(f.path)
        if gi:
            gitignore_suggestions[gi] = True

    data = {
        "findings": [f.__dict__ for f in findings],
        "gitignore": list(gitignore_suggestions.keys()),
        "summary": {"clean": len(findings) == 0, "message": "Human review recommended."}
    }

    out_path = args.out
    if out_path:
        Path(out_path).write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")
        print(f"Wrote {out_path} (findings={len(findings)})")
    else:
        print(json.dumps(data, default=str, indent=2))
    # print concise top-file summary
    files_count = Counter([str(f.path) for f in findings])
    top = files_count.most_common(5)
    if top:
        print("Top files with findings:")
        for p, c in top:
            print(f"  {c}  {p}")


if __name__ == "__main__":
    main()
