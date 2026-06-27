"""Command-line interface for pmpp (protect-my-project)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List

import click

from pmpp.scanner import (
    Finding,
    scan_paths,
    suggest_gitignore_for_path,
    list_repo_files,
)
from pmpp.utils.gitutils import get_changed_files


DEFAULT_MODE = "interactive"





@click.group()
def main():
    """Protect My Project CLI."""


@main.command()
@click.option("--mode", default=DEFAULT_MODE, type=click.Choice(["interactive", "audit"]))
@click.option("--scope", default="changed", type=click.Choice(["changed", "all"]))
@click.option("--autogitignore", "-G", is_flag=True, default=False, help="Auto add suggested entries to .gitignore (requires confirmation).")
@click.option("--format", "out_format", default="text", type=click.Choice(["text", "json"]))
@click.option("--root", default=".", help="Repository root")
@click.option("--llm", default=None, type=click.Choice(["none", "suggest"]), help="Use LLM suggestions for ambiguous items.")
@click.option("--llm-budget", default=1, type=int, help="Max number of ambiguous items to ask the LLM about.")
@click.option("--fast", is_flag=True, default=False, help="Fast mode: only scan changed files and avoid LLM calls.")
@click.option("--dry-run", is_flag=True, default=False, help="Do not modify target repository; show what would change.")
def scan(mode: str, scope: str, autogitignore: bool, out_format: str, root: str, llm: str, llm_budget: int, fast: bool, dry_run: bool) -> None:
    """Scan repository for secrets, gitignore suggestions, and env var candidates."""
    repo = Path(root).resolve()
    if fast:
        scope = "changed"

    if scope == "changed":
        files = get_changed_files(repo)
    else:
        files = list_repo_files(repo)

    findings = scan_paths(files)

    # map to gitignore suggestions
    gitignore_suggestions = {}
    for f in findings:
        gi = suggest_gitignore_for_path(f.path)
        if gi:
            gitignore_suggestions[gi] = True

    # Optional LLM suggestions for ambiguous items
    if llm and llm != "none":
        try:
            from pmpp.utils.llm import batch_suggest
        except Exception:
            batch_suggest = None

        if llm == "suggest" and batch_suggest and not fast:
            ambiguous = []
            for f in findings:
                if (f.detail and f.detail.lower() in ("generic_key", "base64-like")) or f.kind == "pem":
                    ambiguous.append({"path": str(f.path), "line_no": f.line_no, "snippet": f.snippet})
            if ambiguous:
                suggestions = batch_suggest(ambiguous, budget=llm_budget)
                # print concise suggestions
                if out_format == "text":
                    click.echo("\nLLM suggestions (batched):")
                    for k, v in suggestions.items():
                        click.echo(f"- {k}: {v}")

    # output
    if out_format == "json":
        print(json.dumps({
            "findings": [f.__dict__ for f in findings],
            "gitignore": list(gitignore_suggestions.keys()),
            "summary": {
                "clean": len(findings) == 0,
                "message": ("CLI didn't find exposed vulnerabilities - human peer review before merging code is still recommended.")
            }
        }, default=str))
        return

    # text output
    if not findings:
        click.echo("CLI didn't find exposed vulnerabilities - human peer review before merging code is still recommended.")
        return

    click.echo("Findings:")
    for f in findings:
        click.echo(f"- {f.path}:{f.line_no} [{f.kind}] {f.detail or ''}")

    if gitignore_suggestions:
        click.echo("\nSuggested .gitignore entries:")
        for entry in gitignore_suggestions:
            click.echo(f"  {entry}")

        if autogitignore:
            gitignore_file = repo / ".gitignore"
            if not gitignore_file.exists():
                gitignore_file.write_text("")
            existing = gitignore_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            to_add = [e for e in gitignore_suggestions if e not in existing]
            if to_add:
                click.echo("Will add to .gitignore:")
                for e in to_add:
                    click.echo(f"  + {e}")
                if click.confirm("Apply these changes to .gitignore?"):
                    if dry_run:
                        click.echo("Dry-run: would append the above entries to .gitignore (no changes made).")
                    else:
                        with gitignore_file.open("a", encoding="utf-8") as fh:
                            for e in to_add:
                                fh.write(e + "\n")
                        click.echo(".gitignore updated.")


@main.command(name="install-hook")
@click.option("--fail-on", default=None, help="Fail commit on severity (e.g., critical)")
@click.option("--root", default='.', help="Repository root")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be done without writing files")
def install_hook(fail_on: str, root: str, dry_run: bool) -> None:
    """Install a simple git pre-commit hook that runs pmpp in audit mode."""
    repo = Path(root).resolve()
    git_hooks = repo / ".git" / "hooks"
    if not git_hooks.exists():
        click.echo("No .git/hooks directory found; are you in a git repo?")
        return
    click.echo("This will install a local pre-commit hook that runs `pmpp scan --mode audit` before commits.")
    if not click.confirm("Install the pre-commit hook in {0}?".format(str(git_hooks))):
        click.echo("Aborted: no changes made.")
        return
    hook = git_hooks / "pre-commit"
    script = f"#!/usr/bin/env sh\npmpp scan --mode audit\n"
    if dry_run:
        click.echo(f"Dry-run: would write hook to {hook} with contents:\n{script}")
        click.echo("No changes made.")
        return
    hook.write_text(script)
    hook.chmod(0o755)
    click.echo("Installed pre-commit hook (audit mode).")


if __name__ == "__main__":
    main()
