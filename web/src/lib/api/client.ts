import createClient from "openapi-fetch";

import type { components, paths } from "./types";

type RawScanReport = components["schemas"]["ScanReport"];

export type Finding = components["schemas"]["Finding"];
export type Component = components["schemas"]["Component"];
export type ImportRef = components["schemas"]["ImportRef"];
export type ArtifactMeta = components["schemas"]["ArtifactMeta"];
export type Severity = Finding["severity"];
export type ArtifactKind = ArtifactMeta["kind"];
export type Verdict = NonNullable<RawScanReport["verdict"]>;

/**
 * A fully-populated report. Fields with engine-side defaults are optional in the
 * generated schema; {@link normalize} fills them so the UI never juggles `undefined`.
 */
export interface ScanReport {
  artifact_meta: ArtifactMeta;
  components: Component[];
  imports: ImportRef[];
  findings: Finding[];
  score: number;
  verdict: Verdict;
  judges_used: string[];
  summary: string;
}

function normalize(raw: RawScanReport): ScanReport {
  return {
    artifact_meta: raw.artifact_meta,
    components: raw.components ?? [],
    imports: raw.imports ?? [],
    findings: raw.findings ?? [],
    score: raw.score ?? 0,
    verdict: raw.verdict ?? "CLEAN",
    judges_used: raw.judges_used ?? [],
    summary: raw.summary ?? "",
  };
}

/** Thrown when the backend rejects a submission; carries a safe, displayable message. */
export class ScanError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ScanError";
  }
}

// Same-origin in production (FastAPI serves the SPA); the dev server proxies to :8000.
const client = createClient<paths>({ baseUrl: "" });

async function safeDetail(response: Response): Promise<string> {
  try {
    const body = (await response.clone().json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
  } catch {
    /* non-JSON error body — fall through to a generic message */
  }
  return `Scan failed (HTTP ${response.status}).`;
}

/** Run a scan and return the typed JSON ``ScanReport`` (the primary, typed-contract path). */
export async function scanReport(form: FormData): Promise<ScanReport> {
  const { data, error, response } = await client.POST("/scan", {
    // The endpoint takes multipart/form-data; pass the FormData through untouched so the
    // browser sets the multipart boundary (openapi-fetch would otherwise JSON-encode it).
    body: form as unknown as components["schemas"]["Body_scan_scan_post"],
    bodySerializer: (b) => b as unknown as BodyInit,
  });
  if (error !== undefined || data === undefined) {
    throw new ScanError(await safeDetail(response), response.status);
  }
  return normalize(data);
}

/** Re-run the scan asking for SARIF 2.1.0 (used by the Download SARIF button). */
export async function scanSarif(form: FormData): Promise<unknown> {
  const response = await fetch("/scan?format=sarif", { method: "POST", body: form });
  if (!response.ok) {
    throw new ScanError(await safeDetail(response), response.status);
  }
  return response.json();
}
