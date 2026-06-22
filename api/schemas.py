"""Request enums for ``POST /scan``.

Declared as ``str`` enums so FastAPI emits them as named string unions in ``openapi.json``,
which ``openapi-typescript`` turns into precise TypeScript literal types on the client.
"""

from __future__ import annotations

from enum import Enum


class ScanMode(str, Enum):
    """Which of the three input channels a submission uses (exactly one per request)."""

    TEXT = "text"
    ZIP = "zip"
    GIT = "git"


class KindHint(str, Enum):
    """Optional artifact-kind hint for pasted text (picks the default filename)."""

    SKILL = "skill"
    AGENTS = "agents"
    CLAUDE_MD = "claude_md"


class OutputFormat(str, Enum):
    """Response serialization. ``sarif`` can also be selected via the ``Accept`` header."""

    JSON = "json"
    SARIF = "sarif"
