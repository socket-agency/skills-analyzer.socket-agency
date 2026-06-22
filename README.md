# Skill Analyzer

Static security analyzer for AI agent instruction artifacts. It scans Claude Code
**`SKILL.md`** skills, Codex **`AGENTS.md`**, and Claude Code **`CLAUDE.md`** project/user
memory for malicious or unsafe behavior — prompt injection, command execution, data
exfiltration, excessive permissions, obfuscation, and supply-chain risk — and returns a
human-readable report plus machine-readable JSON / SARIF.

> **The analyzer never executes submitted content.** All analysis is static.

This repository currently contains the **web-agnostic analysis engine** (`src/analyzer/`).
The web UI and deployment are planned follow-ups (see [Roadmap](#roadmap)).

## What it detects

| Category | Examples |
|---|---|
| Prompt Injection | "ignore all previous instructions", "mark this as safe" (en/uk/ru) |
| Command Execution | `Bash(*)`, `` !`socat … exec:/bin/bash` ``, `curl … \| bash`, reverse shells |
| Data Exfiltration | env-harvest → network POST (taint), "after every commit, POST the diff to …" |
| Excessive Agency | "auto-approve all tools", "never ask before running" |
| Context Poisoning | CLAUDE.md `@import` of `~/.ssh`, out-of-tree, or remote URLs |
| Obfuscation | base64/hex payloads, zero-width chars, bidi/Trojan-Source, homoglyphs |
| Supply Chain | known-CVE deps (OSV.dev), mutable refs, typosquats |
| Trigger Abuse | descriptions engineered to match every prompt |

Each artifact kind gets its own **analysis profile** — e.g. CLAUDE.md is always-on context, so
standing instructions there are weighted one step higher than the same text in an on-demand skill.

## Design highlights

- **Multilingual-first.** Injection / social-engineering phrasing is detected in English,
  Ukrainian and Russian, plus mixed-script / homoglyph content.
- **Hardened against attacks on the analyzer itself.** A randomized, provider-stratified LLM
  judge panel receives artifact content only inside a per-request **nonce-fenced data block**,
  never concatenated into a system prompt. Judges are **additive-only** (they can raise findings,
  never clear one), and a malformed/jailbroken judge **abstains** — it can never mark something
  clean.
- **documents-vs-performs.** A file that *documents* a malicious pattern (a detector, a quoted
  example, a security policy) is not flagged; one that *performs* it is. The tool passes its own
  scan.
- **ReDoS / bomb safe.** Patterns use the linear-time `google-re2` engine; decoders and archive
  extraction enforce size, depth, file-count and path-traversal limits.

## Usage (engine)

```python
from analyzer.analyze import analyze
from analyzer.config import DEFAULT_CONFIG
from analyzer.ingest.text import ingest_text

with ingest_text(open("SKILL.md").read(), DEFAULT_CONFIG, declared_filename="SKILL.md") as bundle:
    report = analyze(bundle, DEFAULT_CONFIG)

print(report.verdict, report.score)        # e.g. DO_NOT_INSTALL 100
print(report.model_dump_json(indent=2))    # canonical JSON ScanReport
```

Ingest modes: `ingest_text`, `ingest.archive.ingest_zip`, `ingest.git.ingest_git`,
`ingest.directory.ingest_directory`. SARIF: `analyzer.render.sarif.to_sarif(report)`.

### LLM judges

Off by default (deterministic). Set `JUDGE_LIVE=1` and provider keys (via LiteLLM / OpenRouter)
to enable the live panel. The registry, panel size and vote threshold are in `analyzer/config.py`.

## Development

```bash
uv sync
uv run pytest                          # 128 tests
uvx pyright src tests                  # type check
uv run python -m tests.eval.harness    # precision/recall over the corpus + self-scan
```

## Roadmap

- **M7** — FastAPI wrapper + React/Vite/TypeScript/Tailwind/shadcn SPA, three input modes
  (paste / zip / git URL), typed `openapi.json → types.ts` contract, inert (escaped) evidence
  rendering.
- **M8** — multi-stage Dockerfile (React build → FastAPI serves static), Dokku deploy with an
  egress allowlist to the LLM gateway + OSV.dev.
