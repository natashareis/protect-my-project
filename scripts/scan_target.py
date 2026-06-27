#!/usr/bin/env python3
"""Portable runner: run the local `pmpp` package against any target repo without installing.

Usage:
  python scripts/scan_target.py --target /path/to/repo --mode audit --format json

This runs the `pmpp` module from this repository (no install required) against the provided target path.
"""
import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_pmpp(target: str, mode: str, scope: str, fmt: str, fast: bool, autogitignore: bool, extra_args=None):
    cmd = [sys.executable, "-m", "pmpp.cli", "scan", "--root", str(target), "--mode", mode, "--scope", scope]
    if fmt:
        cmd += ["--format", fmt]
    if fast:
        cmd += ["--fast"]
    if autogitignore:
        cmd += ["--autogitignore"]
    if extra_args:
        cmd += extra_args
    # Ensure the pmpp module is discovered by running from the repo root
    return subprocess.run(cmd, cwd=str(REPO_ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Path to the target repository to scan")
    parser.add_argument("--mode", default="interactive", choices=["interactive", "audit"], help="pmpp mode")
    parser.add_argument("--scope", default="changed", choices=["changed", "all"], help="scan scope")
    parser.add_argument("--format", default=None, choices=[None, "json", "pretty"], help="output format for audit")
    parser.add_argument("--fast", action="store_true", help="fast (changed-only) scan")
    parser.add_argument("--autogitignore", action="store_true", help="apply suggested .gitignore entries (interactive only)")
    args, extra = parser.parse_known_args()

    target_path = Path(args.target).resolve()
    if not target_path.exists():
        print(f"Target path does not exist: {target_path}")
        return 2

    rc = run_pmpp(target_path, args.mode, args.scope, args.format, args.fast, args.autogitignore, extra_args=extra)
    return rc.returncode if isinstance(rc, subprocess.CompletedProcess) else 0


if __name__ == "__main__":
    raise SystemExit(main())
