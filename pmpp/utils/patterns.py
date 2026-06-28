"""Default ignore/build/cache patterns used by the scanner.

Each entry is a dict with:
- type: 'dir' | 'suffix' | 'name' | 'path_contains'
- value: string to match
- suggest: suggested .gitignore entry (None means no suggestion)

'dir' entries are also used by the scanner to prune entire directory trees.
'suffix' entries are used by the scanner to skip individual files.
'path_contains' entries are used only for .gitignore suggestions (not directory pruning).
"""

DEFAULT_IGNORE_PATTERNS = [
    # ── Node / JavaScript / TypeScript (all frameworks) ─────────────────────
    {"type": "dir",    "value": "node_modules",     "suggest": "node_modules/"},
    {"type": "dir",    "value": ".cache",            "suggest": ".cache/"},
    {"type": "dir",    "value": ".nyc_output",       "suggest": ".nyc_output/"},
    {"type": "dir",    "value": ".turbo",            "suggest": ".turbo/"},
    {"type": "dir",    "value": ".nx",               "suggest": ".nx/"},
    {"type": "suffix", "value": ".min.js",           "suggest": "*.min.js"},
    {"type": "suffix", "value": ".min.css",          "suggest": "*.min.css"},
    {"type": "suffix", "value": ".map",              "suggest": "*.map"},

    # ── React / Next.js ──────────────────────────────────────────────────────
    {"type": "dir",    "value": ".next",             "suggest": ".next/"},
    {"type": "dir",    "value": "out",               "suggest": "out/"},       # next export

    # ── Angular ──────────────────────────────────────────────────────────────
    {"type": "dir",    "value": ".angular",          "suggest": ".angular/"},

    # ── Vue / Nuxt ───────────────────────────────────────────────────────────
    {"type": "dir",    "value": ".nuxt",             "suggest": ".nuxt/"},
    {"type": "dir",    "value": ".output",           "suggest": ".output/"},   # Nuxt 3

    # ── SvelteKit ────────────────────────────────────────────────────────────
    {"type": "dir",    "value": ".svelte-kit",       "suggest": ".svelte-kit/"},

    # ── Vite / Parcel / Webpack / build tools ────────────────────────────────
    {"type": "dir",    "value": "dist",              "suggest": "dist/"},
    {"type": "dir",    "value": "build",             "suggest": "build/"},
    {"type": "dir",    "value": ".parcel-cache",     "suggest": ".parcel-cache/"},
    {"type": "dir",    "value": ".vite",             "suggest": ".vite/"},
    {"type": "dir",    "value": "storybook-static",  "suggest": "storybook-static/"},

    # ── PHP / Composer / Laravel / Symfony / WordPress ───────────────────────
    {"type": "dir",    "value": "vendor",            "suggest": "vendor/"},
    # Laravel: runtime storage (logs, cache, sessions, uploaded files)
    {"type": "dir",    "value": "storage",           "suggest": "storage/"},
    # Symfony: var/cache and var/log
    {"type": "dir",    "value": "var",               "suggest": "var/"},
    {"type": "path_contains", "value": "bootstrap/cache",   "suggest": "bootstrap/cache/"},
    # WordPress uploaded media
    {"type": "path_contains", "value": "wp-content/uploads", "suggest": "wp-content/uploads/"},

    # ── Ruby / Rails / Bundler ───────────────────────────────────────────────
    {"type": "dir",    "value": ".bundle",           "suggest": ".bundle/"},
    {"type": "dir",    "value": "tmp",               "suggest": "tmp/"},       # Rails tmp
    {"type": "dir",    "value": "log",               "suggest": "log/"},       # Rails logs
    {"type": "dir",    "value": ".sass-cache",       "suggest": ".sass-cache/"},
    {"type": "path_contains", "value": "public/assets", "suggest": "public/assets/"},  # Sprockets
    {"type": "path_contains", "value": "public/packs",  "suggest": "public/packs/"},   # Webpacker

    # ── Python (Django, Flask, FastAPI, etc.) ────────────────────────────────
    {"type": "dir",    "value": "__pycache__",       "suggest": "__pycache__/"},
    {"type": "suffix", "value": ".pyc",              "suggest": "*.pyc"},
    {"type": "dir",    "value": ".venv",             "suggest": ".venv/"},
    {"type": "dir",    "value": ".pytest_cache",     "suggest": ".pytest_cache/"},
    {"type": "dir",    "value": "htmlcov",           "suggest": "htmlcov/"},
    # Django collectstatic output
    {"type": "dir",    "value": "staticfiles",       "suggest": "staticfiles/"},
    # Django user-uploaded media
    {"type": "dir",    "value": "media",             "suggest": "media/"},
    # Flask instance folder (contains instance-local config/db)
    {"type": "dir",    "value": "instance",          "suggest": "instance/"},
    {"type": "dir",    "value": ".eggs",             "suggest": "*.egg-info/"},
    {"type": "path_contains", "value": ".egg-info",       "suggest": "*.egg-info/"},
    {"type": "path_contains", "value": "site-packages",   "suggest": None},

    # ── Java / JVM (Spring Boot, Quarkus, Micronaut, Kotlin, Scala) ──────────
    {"type": "dir",    "value": "target",            "suggest": "target/"},
    {"type": "suffix", "value": ".class",            "suggest": "*.class"},
    {"type": "suffix", "value": ".jar",              "suggest": "*.jar"},
    {"type": "suffix", "value": ".war",              "suggest": "*.war"},
    {"type": "suffix", "value": ".ear",              "suggest": "*.ear"},
    {"type": "dir",    "value": ".gradle",           "suggest": ".gradle/"},
    {"type": "dir",    "value": ".m2",               "suggest": ".m2/"},

    # ── .NET / C# / F# / ASP.NET ─────────────────────────────────────────────
    {"type": "dir",    "value": "obj",               "suggest": "obj/"},
    {"type": "dir",    "value": "packages",          "suggest": "packages/"},  # NuGet
    {"type": "dir",    "value": "TestResults",       "suggest": "TestResults/"},
    {"type": "suffix", "value": ".nupkg",            "suggest": "*.nupkg"},
    {"type": "suffix", "value": ".snupkg",           "suggest": "*.snupkg"},

    # ── Rust ─────────────────────────────────────────────────────────────────
    # target/ already listed above; Cargo.lock skipped by name in scanner

    # ── Go ───────────────────────────────────────────────────────────────────
    # vendor/ already listed above; go.sum skipped by name in scanner

    # ── Infrastructure / DevOps (Terraform, CDK, Serverless, Pulumi) ─────────
    {"type": "dir",    "value": ".terraform",        "suggest": ".terraform/"},
    {"type": "dir",    "value": ".serverless",       "suggest": ".serverless/"},
    {"type": "dir",    "value": "cdk.out",           "suggest": "cdk.out/"},
    {"type": "dir",    "value": ".pulumi",           "suggest": ".pulumi/"},

    # ── General build / test / runtime artifacts ──────────────────────────────
    {"type": "dir",    "value": "coverage",          "suggest": "coverage/"},
    {"type": "dir",    "value": "logs",              "suggest": "logs/"},
    {"type": "suffix", "value": ".log",              "suggest": "*.log"},
    {"type": "suffix", "value": ".exe",              "suggest": "*.exe"},

    # ── IDEs / editors ────────────────────────────────────────────────────────
    {"type": "dir",    "value": ".idea",             "suggest": ".idea/"},
    {"type": "dir",    "value": ".vscode",           "suggest": ".vscode/"},
]
