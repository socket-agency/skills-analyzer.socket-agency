"""Request-scoped scan context (config + OSV query), injected as a FastAPI dependency.

The engine's :class:`AnalyzerConfig` is a frozen dataclass, not a Pydantic model, so it
cannot be a request body. Instead the whole scan configuration is provided through this
dependency. Production uses :data:`analyzer.config.DEFAULT_CONFIG` (which reads ``JUDGE_LIVE``
from the environment at import time) and the live OSV query; tests override the dependency to
disable OSV and stub its query, keeping the suite offline.
"""

from __future__ import annotations

from dataclasses import dataclass

from analyzer.config import DEFAULT_CONFIG, AnalyzerConfig
from analyzer.layers import supply_chain


@dataclass(frozen=True)
class ScanContext:
    """Everything a single scan needs that varies between prod and tests."""

    config: AnalyzerConfig
    osv_query: supply_chain.OsvQuery


def get_scan_context() -> ScanContext:
    """Production scan context: default config + the real OSV lookup.

    ``DEFAULT_CONFIG`` already honors the ``JUDGE_LIVE`` env var, so enabling live judges
    in the deployment is purely a matter of setting that variable plus provider keys.
    """
    return ScanContext(config=DEFAULT_CONFIG, osv_query=supply_chain.query_osv)
