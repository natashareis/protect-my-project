"""Default ignore/build/cache patterns used by the scanner.

Keep this list small and conservative; users can override via a config file later.
Each entry is a dict with:
- type: 'dir' | 'suffix' | 'name' | 'path_contains'
- value: string to match
- suggest: suggested .gitignore entry
"""

DEFAULT_IGNORE_PATTERNS = [
    # Node / JS
    {"type": "dir", "value": "node_modules", "suggest": "node_modules/"},
    {"type": "dir", "value": ".next", "suggest": ".next/"},
    {"type": "dir", "value": "dist", "suggest": "dist/"},
    {"type": "dir", "value": "build", "suggest": "build/"},
    {"type": "dir", "value": ".parcel-cache", "suggest": ".parcel-cache/"},
    {"type": "dir", "value": ".cache", "suggest": ".cache/"},

    # Python
    {"type": "dir", "value": "__pycache__", "suggest": "__pycache__/"},
    {"type": "suffix", "value": ".pyc", "suggest": "*.pyc"},
    {"type": "dir", "value": ".venv", "suggest": ".venv/"},
    {"type": "dir", "value": ".pytest_cache", "suggest": ".pytest_cache/"},

    # Java / JVM
    {"type": "dir", "value": "target", "suggest": "target/"},
    {"type": "suffix", "value": ".class", "suggest": "*.class"},
    {"type": "suffix", "value": ".jar", "suggest": "*.jar"},
    {"type": "dir", "value": ".gradle", "suggest": ".gradle/"},

    # Rust
    {"type": "dir", "value": "target", "suggest": "target/"},

    # Go
    {"type": "dir", "value": "vendor", "suggest": "vendor/"},
    {"type": "dir", "value": "bin", "suggest": "bin/"},
    {"type": "suffix", "value": ".exe", "suggest": "*.exe"},

    # Frontend / bundlers
    {"type": "dir", "value": "dist", "suggest": "dist/"},

    # IDEs / editors
    {"type": "dir", "value": ".idea", "suggest": ".idea/"},
    {"type": "dir", "value": ".vscode", "suggest": ".vscode/"},
]
