# Protect My Project (pmpp)

Small tool to scan a repository for exposed secrets, suggest `.gitignore` entries, and recommend extraction of hard-coded values to environment variables.

Features
- Heuristics-based secret detection (regex + base64 entropy)
- Interactive audit mode with per-item confirmation
- Optional `.gitignore` auto-append with explicit `--autogitignore`
- Pre-commit hook installer (`pmpp install-hook`) that runs in audit mode

## What gets scanned vs skipped

pmpp only scans **source files**. Build outputs, dependency trees, and runtime data are pruned before scanning to keep runs fast and results meaningful.

### Directories that are never traversed

| Stack | Skipped directories |
|---|---|
| **Node / JS / TS** | `node_modules/`, `dist/`, `build/`, `out/`, `.cache/`, `.turbo/`, `.nx/`, `.nyc_output/` |
| **React / Next.js** | `.next/`, `out/` |
| **Angular** | `.angular/` |
| **Vue / Nuxt** | `.nuxt/`, `.output/` |
| **SvelteKit** | `.svelte-kit/` |
| **Vite / Parcel / Storybook** | `.vite/`, `.parcel-cache/`, `storybook-static/` |
| **PHP (Laravel / Symfony / Composer)** | `vendor/`, `storage/`, `var/` |
| **Ruby / Rails / Bundler** | `.bundle/`, `tmp/`, `log/`, `.sass-cache/` |
| **Python (Django / Flask / FastAPI)** | `__pycache__/`, `.venv/`, `venv/`, `env/`, `.pytest_cache/`, `htmlcov/`, `staticfiles/`, `media/`, `instance/`, `.eggs/` |
| **Java / JVM (Spring / Quarkus / Kotlin)** | `target/`, `.gradle/`, `.m2/` |
| **.NET / C# / F#** | `obj/`, `packages/`, `TestResults/` |
| **Rust** | `target/` |
| **Go** | `vendor/` |
| **Infrastructure (Terraform / CDK / Serverless / Pulumi)** | `.terraform/`, `.serverless/`, `cdk.out/`, `.pulumi/` |
| **General** | `coverage/`, `logs/`, `.idea/`, `.vscode/`, `.git/` |

### File types that are always skipped

- **Lock / checksum files** — `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Pipfile.lock`, `composer.lock`, `Gemfile.lock`, `Cargo.lock`, `go.sum`, `mix.lock`, `pubspec.lock`, `packages.lock.json`
- **Compiled / binary** — `.class`, `.jar`, `.war`, `.ear`, `.pyc`, `.exe`, `.dll`, `.so`, `.dylib`, `.o`, `.a`, `.nupkg`
- **Minified / generated** — `.min.js`, `.min.css`, `.map`
- **Media / fonts** — images, audio, video, `.woff`, `.ttf`, `.svg`, etc.
- **Archives** — `.zip`, `.gz`, `.tar`, `.bz2`, `.7z`, `.rar`
- **Database files** — `.db`, `.sqlite`, `.sqlite3`, `.tfstate`
- **Log files** — `.log`
- **Files larger than 512 KB**



Install:

```bash
pip install protect-my-project
```

Usage examples

```bash
# Interactive scan (default)
pmpp scan --mode interactive

# Audit (read-only), JSON output for CI
pmpp scan --mode audit --format json

# Add suggested .gitignore entries (explicit)
pmpp scan --mode interactive --autogitignore

# Install the audit pre-commit hook (opt-in)
pmpp install-hook
```

Advanced flags (low-cost LLM help and fast options)

```bash
# Fast: only scan changed files (default behavior), no LLM calls
pmpp scan --fast

# Use LLM batching to get suggestions for ambiguous items (low token usage)
# Note: LLM calls are optional and off by default for privacy and cost control.
pmpp scan --llm suggest --llm-budget 1

# Combine: audit + LLM suggestions (batched)
pmpp scan --mode audit --llm suggest --llm-budget 1 --format json
```

Config file example (`.pmpp.toml` at repo root)

```toml
[llm]
provider = "suggest"  # none | suggest
budget = 1

[ignore]
enabled = ["node", "python"]
```

Behaviour notes
- Default mode is `interactive` and uses heuristics-only (no network calls).
- `--llm suggest` batches ambiguous items into a single, low-cost suggestion call.
- Use `--fast` or `--scope changed` to limit scanning to changed files for speed and low token usage.

## Getting started with pmpp

**Install from PyPI**

```bash
pip install protect-my-project
```

**Approach 1: Add pmpp as a dev dependency**

Add to your `dev-requirements.txt`:

```
protect-my-project
```

Or in `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = ["protect-my-project"]
```

Install:

```bash
pip install -e ".[dev]"
```

**Approach 2: Local development (from source)**

Install pmpp locally from this repository:

```bash
# From the repository root
python -m pip install -e .
python -m pip install -r requirements.txt
```

Run it:

```bash
# Interactive (recommended)
pmpp scan --mode interactive

# Audit mode for CI (JSON output)
pmpp scan --mode audit --format json
```

**Pre-commit hook (opt-in)**

Install a local pre-commit hook:

```bash
pmpp install-hook
```

This runs `pmpp scan --mode audit` before commits (non-blocking by default).

**Automation and safety**

- pmpp will never modify your target repository without explicit confirmation. All suggested changes are printed; the CLI will prompt before applying them (for example, `--autogitignore` shows suggestions and prompts before updating `.gitignore`, and installing a pre-commit hook requires confirmation).
- Scripts such as `scripts/run_scan_direct.py` and `scripts/run_scan_filtered.py` print JSON reports to stdout by default and will only write a report file when `--out` is explicitly provided. In CI you can redirect output to a file (for example, `pmpp scan --mode audit --format json > pmpp-results.json`).
- Use `--dry-run` on `scan` or `install-hook` to guarantee no writes; the CLI will only show what would change.
- Use `--scope changed` (default) to limit scans to changed/uncommitted files for fast, low-cost runs.
- For LLM-powered suggestions, configure an adapter and set `--llm suggest`.

**Run tests locally**

```bash
pytest -q
```

This repository also includes a simple GitHub Actions workflow in [.github/workflows/tests.yml](.github/workflows/tests.yml) that runs the same test command on pull requests, so your local checks and CI checks stay aligned.

## Using pmpp in your own projects

`pmpp` is available on PyPI. Install it with pip:

```bash
pip install protect-my-project
```

Then use it right away:

```bash
# Interactive scan (default)
pmpp scan --mode interactive

# Audit mode for CI (JSON output)
pmpp scan --mode audit --format json
```

`pmpp` is designed to be used as a dev dependency in your own repositories. Here are two approaches:

**Approach 1: Add pmpp as a dev dependency**

Add to your `dev-requirements.txt`:

```
protect-my-project
```

Or in `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = ["protect-my-project"]
```

Install:

```bash
pip install protect-my-project
```

Run locally:

```bash
pmpp scan --mode interactive
```

Run in CI (see GitHub Actions example below).

**Approach 2: Use pmpp GitHub Action workflow**

Create `.github/workflows/security-scan.yml` in your repository:

```yaml
name: Security Scan with pmpp
on:
  pull_request:
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install pmpp
        run: pip install protect-my-project
      
      - name: Run security scan
        run: pmpp scan --mode audit --format json > pmpp-results.json
      
      - name: Check results
        run: |
          python -c "
          import json
          with open('pmpp-results.json') as f:
              results = json.load(f)
          if not results.get('summary', {}).get('clean', True):
              print('❌ Security vulnerabilities found!')
              exit(1)
          print('✅ No vulnerabilities found')
          "
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: pmpp-scan-results
          path: pmpp-results.json
```

This workflow:
- Runs on every PR and can be manually triggered
- Installs pmpp from PyPI
- Scans the codebase in audit mode
- Blocks the merge if vulnerabilities are found
- Stores results as an artifact for audit trails

## Using pmpp as an agent locally and in CI

**VS Code (interactive)**

1. Open the workspace in VS Code.
2. Run `pmpp: interactive scan` from the Command Palette (`Ctrl+Shift+P` → "Tasks: Run Task").
3. Or use the keybinding `Ctrl+Alt+Shift+P` (after enabling via `python scripts/keybinding_helper.py --apply`).

**Copilot Chat + pmpp**

Run the scan locally, then paste results into Copilot Chat for analysis:

```bash
pmpp scan --mode interactive --scope changed
```

**VS Code keybinding helper (opt-in)**

```bash
python scripts/keybinding_helper.py --apply
```

This copies `.vscode/keybindings.example.json` to your user settings (with confirmation).

Scan another project without installing

If you don't want to add `pyproject.toml` or `setup.py` to a target project, run the scanner from this repository against any target path using the portable runner script. From this repo root:

```bash
# run the runner against another repository (no install required in the target)
python scripts/scan_target.py --target C:/path/to/other-repo --mode audit --scope all --format json
```

Alternatively you can invoke the local module directly (also from this repo root):

```bash
python -m pmpp.cli scan --root C:/path/to/other-repo --mode audit --scope all --format json
```

Both approaches let you scan arbitrary repositories without modifying them.

Notes
- The GitHub action uses heuristics-only scanning by default to avoid external network calls and token usage.
- To enable LLM suggestions in CI you must wire an adapter and provide credentials securely via repository secrets (not recommended by default).

Development

Run unit tests:

```bash
pytest -q
```
