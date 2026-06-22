"""CLAUDE.md ``@import`` graph resolution inside the sandbox (§4.1).

Imports are classified in-tree / out-of-tree / remote. In-tree targets are
followed one hop (``config.import_follow_depth``) so an injection can't hide a
single hop away; out-of-tree (``@~/…``, ``@/…``, ``@../…``) and remote (``@http…``)
targets are recorded but never read.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

import re2

from analyzer.bundle import Bundle
from analyzer.config import AnalyzerConfig
from analyzer.models import ImportKind, ImportRef

# @ at start-of-text or after whitespace, then a non-whitespace token. Linear in re2.
_IMPORT_RE = re2.compile(r"(?:^|\s)@([^\s]+)")
_TRAILING = ",;:)]}>\"'"


def _looks_like_path(token: str) -> bool:
    return "/" in token or "." in token or token.startswith("~") or "://" in token


def _is_within(root: Path, target: Path) -> bool:
    return root == target or root in target.parents


def _classify(
    token: str, importing_dir: Path, root: Path
) -> tuple[ImportKind, str, Path | None]:
    if token.startswith(("http://", "https://")) or "://" in token:
        return ImportKind.REMOTE, token, None
    if token.startswith("~") or token.startswith("/"):
        return ImportKind.OUT_OF_TREE, token, None

    candidate = (root / importing_dir / token).resolve()
    if _is_within(root.resolve(), candidate):
        target = str(candidate.relative_to(root.resolve()))
        return ImportKind.IN_TREE, target, candidate
    return ImportKind.OUT_OF_TREE, token, None


def resolve_imports(
    bundle: Bundle, primary_path: Path | str, config: AnalyzerConfig
) -> list[ImportRef]:
    root = bundle.root.resolve()
    results: list[ImportRef] = []
    seen: set[tuple[str, ImportKind]] = set()
    queue: deque[tuple[Path, int]] = deque([(Path(primary_path), 0)])
    visited_files: set[Path] = set()

    while queue:
        file_rel, depth = queue.popleft()
        if file_rel in visited_files:
            continue
        visited_files.add(file_rel)
        try:
            content = bundle.read_text(file_rel)
        except (OSError, ValueError):
            continue

        for token in _IMPORT_RE.findall(content):
            token = token.rstrip(_TRAILING)
            if not _looks_like_path(token):
                continue
            kind, target, abs_path = _classify(token, file_rel.parent, root)
            resolved = bool(kind is ImportKind.IN_TREE and abs_path and abs_path.is_file())

            key = (target, kind)
            if key not in seen:
                seen.add(key)
                results.append(ImportRef(raw=f"@{token}", target=target, kind=kind, resolved=resolved))

            if resolved and abs_path is not None and depth < config.import_follow_depth:
                queue.append((abs_path.relative_to(root), depth + 1))

    return results
