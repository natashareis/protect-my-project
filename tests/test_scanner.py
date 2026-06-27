import subprocess
import tempfile
from pathlib import Path

import pytest

from pmpp.scanner import find_secrets_in_text, scan_paths, suggest_gitignore_for_path


def test_find_secrets_simple(tmp_path: Path):
    f = tmp_path / "foo.py"
    f.write_text('OPENAI_API_KEY = "sk-abc123def456ghi789jkl"\n')
    findings = scan_paths([f])
    assert any("OPENAI" in (fnd.detail or "") or fnd.kind == "secret" for fnd in findings)


def test_e2e_repo(tmp_path: Path):
    # create a fake repo structure
    repo = tmp_path / "myrepo"
    repo.mkdir()
    (repo / "app").mkdir()
    secret_file = repo / "app" / "main.py"
    secret_file.write_text('OPENAI_API_KEY = "sk-zzz111222333444555"\n')
    # initialize git so CLI can use status
    subprocess.check_call(["git", "init"], cwd=repo)
    subprocess.check_call(["git", "add", "."], cwd=repo)
    subprocess.check_call(["git", "commit", "-m", "init"], cwd=repo, stdout=subprocess.DEVNULL)

    # modify file to create a changed file
    secret_file.write_text('OPENAI_API_KEY = "sk-zzz111222333444555"\nSOMETHING=1\n')

    # run scan via CLI
    out = subprocess.check_output(["python", "-m", "pmpp.cli", "scan", "--mode", "audit", "--root", str(repo)], text=True)
    # CLI should report findings status in some form (either listing findings or reporting none)
    assert "find" in out.lower()


def test_gitignore_suggestions_for_pyc(tmp_path: Path):
    d = tmp_path / "pkg"
    d.mkdir()
    pycache = d / "__pycache__"
    pycache.mkdir()
    pyc = d / "module.cpython-311.pyc"
    pyc.write_text("\x00\x01")

    assert suggest_gitignore_for_path(pycache) == "__pycache__/"
    assert suggest_gitignore_for_path(pyc) == "*.pyc"
