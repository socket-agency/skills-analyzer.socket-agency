"""Frontmatter parsing tests — safe_load only, malformed never crashes (§4.1, §6.4)."""

from __future__ import annotations

from dataclasses import replace

from analyzer.config import DEFAULT_CONFIG
from analyzer.parsing.frontmatter import parse_frontmatter


def test_parses_valid_frontmatter_and_body():
    text = "---\nname: my-skill\nallowed-tools: Read, Grep\n---\nThe body here.\n"
    fm = parse_frontmatter(text, DEFAULT_CONFIG)
    assert fm.present and not fm.malformed
    assert fm.data == {"name": "my-skill", "allowed-tools": "Read, Grep"}
    assert fm.body.strip() == "The body here."


def test_no_frontmatter_is_not_malformed():
    fm = parse_frontmatter("# Just a CLAUDE.md\nconventions here", DEFAULT_CONFIG)
    assert not fm.present
    assert not fm.malformed
    assert fm.data is None
    assert "conventions here" in fm.body


def test_malformed_yaml_does_not_crash():
    text = "---\nname: [unclosed\n---\nbody"
    fm = parse_frontmatter(text, DEFAULT_CONFIG)
    assert fm.present
    assert fm.malformed
    assert fm.data is None


def test_yaml_tag_object_construction_is_neutralized():
    """safe_load must refuse arbitrary object construction — never execute it."""
    text = "---\nevil: !!python/object/apply:os.system ['echo pwned']\n---\nbody"
    fm = parse_frontmatter(text, DEFAULT_CONFIG)
    # neutralized: treated as malformed, no code ran, no object built
    assert fm.malformed
    assert fm.data is None


def test_oversized_frontmatter_is_rejected_as_malformed():
    cfg = replace(DEFAULT_CONFIG, max_yaml_bytes=64)
    text = "---\n" + ("k: v\n" * 100) + "---\nbody"
    fm = parse_frontmatter(text, cfg)
    assert fm.malformed
    assert fm.data is None


def test_non_mapping_frontmatter_is_malformed():
    text = "---\n- just\n- a\n- list\n---\nbody"
    fm = parse_frontmatter(text, DEFAULT_CONFIG)
    assert fm.malformed
    assert fm.data is None
