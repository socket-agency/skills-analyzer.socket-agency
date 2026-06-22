"""Artifact-kind detection, profile routing and component classification (§4.1).

Detecting the kind selects an *analysis profile* — the three kinds have different
attack surfaces, so this routing decision shapes the whole downstream pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from analyzer.bundle import Bundle
from analyzer.config import AnalyzerConfig
from analyzer.models import ArtifactKind, Component, ComponentType

# filename -> kind, in priority order (a skill folder that also ships a CLAUDE.md
# is still primarily a skill)
_KIND_BY_FILENAME: tuple[tuple[str, ArtifactKind], ...] = (
    ("SKILL.md", ArtifactKind.SKILL),
    ("AGENTS.md", ArtifactKind.AGENTS),
    ("CLAUDE.md", ArtifactKind.CLAUDE_MD),
)

_LANG_BY_SUFFIX: dict[str, str] = {
    ".py": "python",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".rb": "ruby",
    ".pl": "perl",
    ".ps1": "powershell",
    ".md": "markdown",
    ".txt": "text",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".toml": "toml",
}

_EXECUTABLE_LANGS = {"python", "shell", "javascript", "typescript", "ruby", "perl", "powershell"}


@dataclass
class Discovery:
    kind: ArtifactKind
    primary_path: Path
    scope: str | None = None
    components: list[Component] = field(default_factory=list)

    def primary_is_doc(self) -> bool:
        """True when the primary artifact is a markdown/text instruction file.

        Distinguishes a real instruction artifact (SKILL.md / CLAUDE.md / AGENTS.md)
        from a code file that became 'primary' only via fallback (e.g. a self-scan of
        source). Instruction-body analysis must not run on source code.
        """
        primary = str(self.primary_path)
        for comp in self.components:
            if comp.path == primary:
                return comp.language in ("markdown", "text", None)
        return primary.lower().endswith((".md", ".markdown", ".txt"))


def _language_for(path: Path) -> str | None:
    return _LANG_BY_SUFFIX.get(path.suffix.lower())


def _classify(relpath: Path, primary: Path) -> Component:
    parts = relpath.parts
    lang = _language_for(relpath)
    executable = lang in _EXECUTABLE_LANGS if lang else False

    if relpath == primary:
        ctype = ComponentType.MANIFEST
    elif "scripts" in parts or executable:
        ctype = ComponentType.SCRIPT
    elif "references" in parts:
        ctype = ComponentType.REFERENCE
    elif "assets" in parts:
        ctype = ComponentType.ASSET
    else:
        ctype = ComponentType.OTHER

    return Component(path=str(relpath), type=ctype, language=lang, executable=executable)


def _find_primary(bundle: Bundle) -> tuple[Path, ArtifactKind] | None:
    """Pick the primary artifact across a bundle, by filename priority then shallowness."""
    files = list(bundle.iter_files())
    for filename, kind in _KIND_BY_FILENAME:
        matches = [p for p in files if p.name == filename]
        if matches:
            matches.sort(key=lambda p: (len(p.parts), str(p)))
            return matches[0], kind
    return None


def _claude_md_scope(primary: Path) -> str:
    parts = primary.parts
    if len(parts) == 1:  # ./CLAUDE.md
        return "project"
    if parts[0] == ".claude" and len(parts) == 2:  # .claude/CLAUDE.md
        return "project"
    return "nested"


def discover(bundle: Bundle, config: AnalyzerConfig) -> Discovery:
    found = _find_primary(bundle)
    if found is None:
        # nothing recognized — fall back to the declared primary or first file as a skill-ish doc
        primary = bundle.primary_path or next(iter(bundle.iter_files()), Path("PASTED.md"))
        kind = ArtifactKind.SKILL
    else:
        primary, kind = found

    scope = _claude_md_scope(primary) if kind is ArtifactKind.CLAUDE_MD else None
    components = [_classify(p, primary) for p in bundle.iter_files()]
    return Discovery(kind=kind, primary_path=primary, scope=scope, components=components)
