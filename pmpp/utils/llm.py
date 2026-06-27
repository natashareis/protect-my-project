"""Lightweight LLM adapter placeholders (utilities).

These functions are placeholders that implement batching and caching
behaviour locally without making external calls. Real adapters will be
implemented later and wired behind the same interface.
"""
from __future__ import annotations

from typing import Dict, Iterable, List


def batch_suggest(ambiguous_items: Iterable[Dict], budget: int = 1) -> Dict[str, str]:
    """Return simple suggested remediation for each ambiguous item.

    ambiguous_items: iterable of dicts {"path": str, "line_no": int, "snippet": str}
    Returns mapping of path->short suggestion.
    This is a stub to minimize tokens; real implementations will call external LLMs.
    """
    suggestions: Dict[str, str] = {}
    items = list(ambiguous_items)
    # Respect budget: only process up to `budget` items (cheap heuristic)
    for itm in items[: max(1, budget)]:
        key = f"{itm.get('path')}:{itm.get('line_no')}"
        suggestions[key] = "Consider redacting this token or moving it to an environment variable."
    return suggestions
