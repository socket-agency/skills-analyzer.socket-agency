"""FastAPI app wrapping the Skill Analyzer engine.

One endpoint, ``POST /scan``, accepts a single submission via one of three modes
(pasted text, uploaded ``.zip``, or a git URL) and returns a canonical ``ScanReport``
(JSON by default, SARIF 2.1.0 on request). In production it also serves the built React
SPA as static files. The engine is blocking (file IO, a subprocess git clone, a judge
thread-pool), so every scan runs off the event loop via ``anyio.to_thread.run_sync``.

Safety properties carried here from the spec (§6.5):
- Submissions are **ephemeral**: every ``Bundle`` is cleaned up in a ``finally``.
- Submitted content and secrets are **never logged**.
- ``ingest_git`` is called with ``allow_local=False`` so web input can't read the host FS.
"""

from __future__ import annotations

import logging
from pathlib import Path

import anyio.to_thread
from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from analyzer.analyze import analyze
from analyzer.bundle import Bundle
from analyzer.ingest.archive import IngestError, ingest_zip
from analyzer.ingest.git import ingest_git
from analyzer.ingest.text import ingest_text
from analyzer.models import ScanReport
from analyzer.render.sarif import to_sarif
from api.deps import ScanContext, get_scan_context
from api.schemas import KindHint, OutputFormat, ScanMode

# Configure logging at the app (not in the web-free engine). uvicorn doesn't attach a
# root handler, so without this the engine's WARN logs (e.g. a judge that failed) and our
# own INFO lines would be dropped instead of reaching the container's stdout/Dokku logs.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
for _noisy in ("httpx", "httpcore", "litellm", "LiteLLM"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)

logger = logging.getLogger("api.scan")

app = FastAPI(
    title="Skill Analyzer",
    version="0.1.0",
    summary="Static security analysis for AI agent instruction artifacts.",
)

_SARIF_MEDIA_TYPE = "application/sarif+json"
_WEB_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"


def _run_scan(
    mode: ScanMode,
    *,
    content: str | None,
    url: str | None,
    data: bytes | None,
    filename: str | None,
    kind_hint: KindHint | None,
    ctx: ScanContext,
) -> ScanReport:
    """Ingest the submission and analyze it. BLOCKING — run via ``anyio.to_thread``.

    Owns the ``Bundle`` lifecycle: the temp sandbox is always removed, even on error.
    """
    config = ctx.config
    if mode is ScanMode.TEXT:
        assert content is not None
        bundle: Bundle = ingest_text(
            content, config, declared_filename=filename, kind_hint=kind_hint.value if kind_hint else None
        )
    elif mode is ScanMode.ZIP:
        assert data is not None
        bundle = ingest_zip(data, config, declared_filename=filename)
    else:  # ScanMode.GIT
        assert url is not None
        bundle = ingest_git(url, config)  # allow_local=False: never expose the host FS
    try:
        return analyze(bundle, config, osv_query=ctx.osv_query)
    finally:
        bundle.cleanup()


async def _read_capped(upload: UploadFile, cap: int) -> bytes | None:
    """Read an upload in bounded chunks, bailing out as soon as it exceeds ``cap``.

    Returns ``None`` if the upload is too large — so an attacker who omits ``Content-Length``
    can't make us buffer an unbounded body before the size check (limits BEFORE ingest).
    """
    chunks: list[bytes] = []
    total = 0
    while chunk := await upload.read(1024 * 1024):
        total += len(chunk)
        if total > cap:
            return None
        chunks.append(chunk)
    return b"".join(chunks)


def _wants_sarif(fmt: str | None, accept: str | None) -> bool:
    """SARIF is selected by ``?format=sarif`` or an ``Accept: application/sarif+json`` header."""
    if fmt and fmt.lower() == OutputFormat.SARIF.value:
        return True
    return _SARIF_MEDIA_TYPE in (accept or "")


@app.get("/api/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/scan", response_model=ScanReport)
async def scan(
    request: Request,
    mode: ScanMode = Form(..., description="Which input channel this submission uses."),
    content: str | None = Form(None, description="Artifact body (mode=text)."),
    url: str | None = Form(None, description="Remote git URL (mode=git)."),
    kind_hint: KindHint | None = Form(None, description="Artifact-kind hint for pasted text."),
    filename: str | None = Form(None, description="Declared filename for pasted text or a zip."),
    file: UploadFile | None = File(None, description="Uploaded .zip bundle (mode=zip)."),
    fmt: str | None = Query(None, alias="format", description="Set to 'sarif' for SARIF 2.1.0."),
    ctx: ScanContext = Depends(get_scan_context),
) -> JSONResponse:
    """Scan one artifact submission and return a ``ScanReport`` (JSON or SARIF)."""
    cap = ctx.config.max_total_bytes
    data: bytes | None = None

    # --- validate the mode's required field and enforce size caps BEFORE ingest ---
    if mode is ScanMode.TEXT:
        if not content:
            raise HTTPException(status_code=400, detail="mode=text requires a 'content' field.")
        if len(content.encode("utf-8", errors="ignore")) > cap:
            raise HTTPException(status_code=413, detail="Submission exceeds the size limit.")
    elif mode is ScanMode.ZIP:
        if file is None:
            raise HTTPException(status_code=400, detail="mode=zip requires a 'file' upload.")
        if file.size is not None and file.size > cap:
            raise HTTPException(status_code=413, detail="Submission exceeds the size limit.")
        data = await _read_capped(file, cap)
        if data is None:
            raise HTTPException(status_code=413, detail="Submission exceeds the size limit.")
        filename = filename or file.filename
    else:  # ScanMode.GIT
        if not url:
            raise HTTPException(status_code=400, detail="mode=git requires a 'url' field.")

    try:
        report = await anyio.to_thread.run_sync(
            lambda: _run_scan(
                mode,
                content=content,
                url=url,
                data=data,
                filename=filename,
                kind_hint=kind_hint,
                ctx=ctx,
            )
        )
    except IngestError as exc:
        # Safe, generic message — never echo a stack trace or submitted content.
        logger.info("ingest rejected: mode=%s reason=%s", mode.value, type(exc).__name__)
        raise HTTPException(status_code=400, detail=f"Could not ingest submission: {exc}") from None

    logger.info("scan completed: mode=%s verdict=%s score=%s", mode.value, report.verdict.value, report.score)

    accept = request.headers.get("accept")
    if _wants_sarif(fmt, accept):
        return JSONResponse(content=to_sarif(report), media_type=_SARIF_MEDIA_TYPE)
    return JSONResponse(content=report.model_dump(mode="json"))


# --- SPA static serving (production only; absent in dev/tests) ------------------------------
# Mounted last so it never shadows /scan or /api/*. Client-side routes fall back to index.html.
if _WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=_WEB_DIST, html=True), name="spa")
