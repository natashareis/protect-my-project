#!/usr/bin/env python3
"""Helper to install the example VS Code keybinding into the user's VS Code keybindings location.

Usage:
  python scripts/keybinding_helper.py         # prints instructions
  python scripts/keybinding_helper.py --apply # copies example into your VS Code User keybindings.json (prompts first)

This script is intentionally opt-in and will never run automatically.
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path


EXAMPLE = Path(__file__).resolve().parents[1] / ".vscode" / "keybindings.example.json"


def user_keybindings_path():
    if sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA")
        if not appdata:
            return None
        return Path(appdata) / "Code" / "User" / "keybindings.json"
    elif sys.platform == "darwin":
        home = Path.home()
        return home / "Library" / "Application Support" / "Code" / "User" / "keybindings.json"
    else:
        home = Path.home()
        return home / ".config" / "Code" / "User" / "keybindings.json"


def print_instructions():
    print("pmpp keybinding helper")
    print()
    print("To enable the suggested keybinding locally, do one of the following:")
    print("  1) Copy `.vscode/keybindings.example.json` into your VS Code User keybindings file:")
    print("")
    print("     cp .vscode/keybindings.example.json <your VS Code user keybindings path>")
    print()
    print("  2) Or open `.vscode/keybindings.example.json`, copy its contents, and paste into your user keybindings (Preferences: Open Keyboard Shortcuts (JSON))")
    print()
    p = user_keybindings_path()
    if p:
        print(f"Detected likely user keybindings path: {p}")
    else:
        print("Could not detect your VS Code user folder automatically; please use the UI to paste the example.")


def apply_copy(force=False):
    dest = user_keybindings_path()
    if not dest:
        print("Could not detect user keybindings path for this platform.")
        return 2
    if not EXAMPLE.exists():
        print(f"Example keybindings not found at {EXAMPLE}")
        return 2
    dest_parent = dest.parent
    dest_parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        print(f"A keybindings file already exists at {dest}.")
        resp = input("Overwrite it? [y/N]: ").strip().lower()
        if resp != "y":
            print("Aborted. No changes made.")
            return 1
    try:
        shutil.copy2(EXAMPLE, dest)
        print(f"Copied example keybindings to {dest}")
        return 0
    except Exception as e:
        print("Failed to copy keybindings:", e)
        return 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Copy example into VS Code user keybindings (prompts)")
    parser.add_argument("--force", action="store_true", help="Overwrite without prompting when used with --apply")
    args = parser.parse_args()
    if args.apply:
        return apply_copy(force=args.force)
    print_instructions()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
