"""YAML frontmatter parsing, hardened against untrusted input (§4.1, §6.4).

- ``yaml.safe_load`` only — never ``load`` — so object/tag construction can't execute.
- A cheap linear flow-nesting pre-check rejects deep-recursion bombs (``[[[[…``)
  before they reach the parser; ``RecursionError`` from block-style nesting is also
  caught and reported as malformed.
- Size cap on the frontmatter block; fences split line-by-line (no regex, ReDoS-proof).
- Any malformation is reported as a flag, never raised to the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml

from analyzer.config import AnalyzerConfig

_FENCE = "---"


@dataclass
class Frontmatter:
    present: bool
    malformed: bool
    data: dict[str, Any] | None
    body: str
    raw: str | None


def _split_fences(text: str) -> tuple[str, str] | None:
    """Return (raw_frontmatter, body) if a leading ``---`` block exists, else None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != _FENCE:
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == _FENCE:
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1 :])
    return None  # unterminated fence — treat as no frontmatter


def _max_flow_depth(raw: str) -> int:
    """Max nesting depth of YAML flow collections — a cheap linear ReDoS-free scan."""
    depth = max_depth = 0
    for ch in raw:
        if ch in "[{":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch in "]}":
            depth = max(0, depth - 1)
    return max_depth


def _max_indent(raw: str) -> int:
    """Max leading-whitespace run — bounds block-style nesting depth."""
    return max((len(line) - len(line.lstrip(" ")) for line in raw.splitlines()), default=0)


def parse_frontmatter(text: str, config: AnalyzerConfig) -> Frontmatter:
    split = _split_fences(text)
    if split is None:
        return Frontmatter(present=False, malformed=False, data=None, body=text, raw=None)

    raw, body = split
    malformed = Frontmatter(present=True, malformed=True, data=None, body=body, raw=raw)

    if len(raw.encode("utf-8", errors="ignore")) > config.max_yaml_bytes:
        return malformed
    if _max_flow_depth(raw) > config.max_yaml_depth or _max_indent(raw) > config.max_yaml_depth:
        return malformed

    try:
        data = yaml.safe_load(raw)
    except (yaml.YAMLError, RecursionError):
        return malformed

    if not isinstance(data, dict):
        return malformed

    return Frontmatter(present=True, malformed=False, data=data, body=body, raw=raw)
