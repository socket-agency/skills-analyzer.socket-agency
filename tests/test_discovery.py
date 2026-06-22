"""Artifact-kind routing + component classification tests (M1 gate)."""

from __future__ import annotations

import io
import zipfile

from analyzer.config import DEFAULT_CONFIG
from analyzer.discovery import discover
from analyzer.ingest.archive import ingest_zip
from analyzer.ingest.text import ingest_text
from analyzer.models import ArtifactKind, ComponentType


def _zip(entries: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


def test_detects_skill_from_filename():
    with ingest_text("---\nname: x\n---\nbody", DEFAULT_CONFIG, declared_filename="SKILL.md") as b:
        d = discover(b, DEFAULT_CONFIG)
        assert d.kind is ArtifactKind.SKILL


def test_detects_agents_from_filename():
    with ingest_text("do things", DEFAULT_CONFIG, declared_filename="AGENTS.md") as b:
        assert discover(b, DEFAULT_CONFIG).kind is ArtifactKind.AGENTS


def test_detects_claude_md_from_filename():
    with ingest_text("# conventions", DEFAULT_CONFIG, declared_filename="CLAUDE.md") as b:
        assert discover(b, DEFAULT_CONFIG).kind is ArtifactKind.CLAUDE_MD


def test_zip_skill_classifies_components():
    data = _zip(
        {
            "SKILL.md": b"---\nname: x\n---\nbody",
            "scripts/run.py": b"print(1)",
            "references/notes.md": b"docs",
            "assets/logo.png": b"\x89PNG",
        }
    )
    with ingest_zip(data, DEFAULT_CONFIG) as b:
        d = discover(b, DEFAULT_CONFIG)
        assert d.kind is ArtifactKind.SKILL
        by_path = {c.path: c for c in d.components}
        assert by_path["scripts/run.py"].type is ComponentType.SCRIPT
        assert by_path["scripts/run.py"].executable is True
        assert by_path["scripts/run.py"].language == "python"
        assert by_path["references/notes.md"].type is ComponentType.REFERENCE
        assert by_path["assets/logo.png"].type is ComponentType.ASSET


def test_claude_md_dot_claude_scope_is_project():
    data = _zip({".claude/CLAUDE.md": b"# rules"})
    with ingest_zip(data, DEFAULT_CONFIG) as b:
        d = discover(b, DEFAULT_CONFIG)
        assert d.kind is ArtifactKind.CLAUDE_MD
        assert d.scope == "project"


def test_claude_md_nested_scope():
    data = _zip({"src/CLAUDE.md": b"# nested rules"})
    with ingest_zip(data, DEFAULT_CONFIG) as b:
        d = discover(b, DEFAULT_CONFIG)
        assert d.kind is ArtifactKind.CLAUDE_MD
        assert d.scope == "nested"


def test_skill_takes_priority_over_claude_md_in_same_bundle():
    data = _zip({"SKILL.md": b"---\nname: x\n---\nb", "CLAUDE.md": b"# rules"})
    with ingest_zip(data, DEFAULT_CONFIG) as b:
        assert discover(b, DEFAULT_CONFIG).kind is ArtifactKind.SKILL


def test_malformed_skill_does_not_crash_discovery():
    with ingest_text("---\nbad: [\n---\nb", DEFAULT_CONFIG, declared_filename="SKILL.md") as b:
        d = discover(b, DEFAULT_CONFIG)
        assert d.kind is ArtifactKind.SKILL  # still routed by filename
