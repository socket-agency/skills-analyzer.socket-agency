import { AlertTriangle, ScanLine } from "lucide-react";
import * as React from "react";

import { ReportView } from "@/components/ReportView";
import { ScanForm } from "@/components/ScanForm";
import { ScanError, scanReport, scanSarif, type ScanReport } from "@/lib/api/client";

export default function App() {
  const [report, setReport] = React.useState<ScanReport | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const lastForm = React.useRef<FormData | null>(null);

  async function handleSubmit(form: FormData) {
    lastForm.current = form;
    setBusy(true);
    setError(null);
    try {
      setReport(await scanReport(form));
    } catch (err) {
      setReport(null);
      setError(err instanceof ScanError ? err.message : "Unexpected error running the scan.");
    } finally {
      setBusy(false);
    }
  }

  function requestSarif() {
    if (!lastForm.current) return Promise.reject(new Error("Nothing to export."));
    return scanSarif(lastForm.current);
  }

  return (
    <div className="mx-auto min-h-full max-w-4xl px-5 py-10">
      <header className="mb-8 flex items-center gap-3">
        <div className="flex size-11 items-center justify-center rounded-md border border-scan/40 bg-scan/10">
          <ScanLine className="size-6 text-scan" aria-hidden />
        </div>
        <div>
          <h1 className="font-mono text-xl font-bold tracking-tight text-ink">
            Skill<span className="text-scan">Analyzer</span>
          </h1>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-faint">
            static security scanner · skill / agents / claude.md
          </p>
        </div>
      </header>

      <p className="mb-6 max-w-2xl text-sm leading-relaxed text-muted">
        Scan AI agent instruction artifacts for prompt injection, command execution, data
        exfiltration, excessive permissions, obfuscation and supply-chain risk. The analyzer{" "}
        <span className="text-ink">never executes</span> submitted content — all analysis is static.
      </p>

      <ScanForm busy={busy} onSubmit={handleSubmit} />

      {error ? (
        <div
          role="alert"
          className="mt-6 flex items-start gap-2 rounded-md border border-danger/40 bg-danger/10 p-4 text-sm text-danger"
        >
          <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden />
          {/* server-supplied message is plain text; rendered inert */}
          <span>{error}</span>
        </div>
      ) : null}

      {report ? (
        <div className="mt-8">
          <ReportView report={report} onRequestSarif={requestSarif} />
        </div>
      ) : null}

      <footer className="mt-12 border-t border-line pt-5 font-mono text-[11px] text-faint">
        Submissions are ephemeral — never persisted or logged. JSON + SARIF 2.1.0 output.
      </footer>
    </div>
  );
}
