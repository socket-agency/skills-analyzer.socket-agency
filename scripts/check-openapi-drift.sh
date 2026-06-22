#!/usr/bin/env bash
# Fail if the committed typed contract is stale.
#
# Regenerates web/openapi.json (from the live FastAPI schema) and web/src/lib/api/types.ts
# (from that openapi.json), then checks for any git diff. Run in CI after `uv sync` and
# `bun install`. The pytest `tests/test_openapi_contract.py` covers the openapi.json half on
# its own; this script also covers the generated TypeScript types.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "→ regenerating web/openapi.json from app.openapi()"
uv run python -m api.dump_openapi

echo "→ regenerating web/src/lib/api/types.ts"
( cd web && bun run gen:api )

if ! git diff --exit-code -- web/openapi.json web/src/lib/api/types.ts; then
  echo
  echo "✗ typed contract is out of date." >&2
  echo "  Run: uv run python -m api.dump_openapi && (cd web && bun run gen:api)" >&2
  echo "  Then commit web/openapi.json and web/src/lib/api/types.ts." >&2
  exit 1
fi

echo "✓ typed contract is up to date."
