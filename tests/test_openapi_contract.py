"""Contract drift guard: the committed openapi.json must match the live FastAPI schema.

Runs in the normal suite (no CI infra needed). If the API changes without regenerating
``web/openapi.json`` (and therefore ``types.ts``), this fails — pointing at the fix command.
"""

from __future__ import annotations

import json

from api.dump_openapi import OPENAPI_PATH, render
from api.main import app


def test_committed_openapi_matches_live_schema():
    assert OPENAPI_PATH.exists(), "run: uv run python -m api.dump_openapi"
    committed = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
    assert committed == app.openapi(), "openapi.json is stale — run: uv run python -m api.dump_openapi"


def test_render_is_deterministic_and_terminated():
    out = render()
    assert out.endswith("\n")
    # parses and round-trips
    assert json.loads(out) == app.openapi()


def test_scan_path_is_documented():
    schema = app.openapi()
    assert "/scan" in schema["paths"]
    assert "post" in schema["paths"]["/scan"]
