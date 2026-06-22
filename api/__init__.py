"""FastAPI delivery layer for the Skill Analyzer engine.

This package *imports* :mod:`analyzer`; the engine never imports back. Keeping the
dependency one-directional is what lets the analyzer stay web-free and unit-testable
in isolation (see the root ``CLAUDE.md`` architecture notes).
"""
