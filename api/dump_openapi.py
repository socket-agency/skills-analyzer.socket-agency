"""Write ``web/openapi.json`` from ``app.openapi()`` without booting a server.

This is the source of the typed client contract: the committed ``openapi.json`` feeds
``openapi-typescript`` (the ``web`` pre-build step) which generates ``src/lib/api/types.ts``.
Run as::

    uv run python -m api.dump_openapi

A pytest (``tests/test_openapi_contract.py``) asserts the committed file matches the live
schema, so drift fails CI without any running server.
"""

from __future__ import annotations

import json
from pathlib import Path

from api.main import app

OPENAPI_PATH = Path(__file__).resolve().parent.parent / "web" / "openapi.json"


def render() -> str:
    """Return the OpenAPI document as deterministic, newline-terminated JSON."""
    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    OPENAPI_PATH.parent.mkdir(parents=True, exist_ok=True)
    OPENAPI_PATH.write_text(render(), encoding="utf-8")
    print(f"wrote {OPENAPI_PATH}")


if __name__ == "__main__":
    main()
