import { Download, Gavel } from "lucide-react";

import { ComponentsTable } from "@/components/ComponentsTable";
import { FindingsList } from "@/components/FindingsList";
import { ImportsList } from "@/components/ImportsList";
import { KindBadge } from "@/components/KindBadge";
import { VerdictBanner } from "@/components/VerdictBanner";
import { Button } from "@/components/ui/button";
import type { ScanReport } from "@/lib/api/client";

function downloadBlob(filename: string, contents: string, type: string) {
  const url = URL.createObjectURL(new Blob([contents], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export interface ReportViewProps {
  report: ScanReport;
  /** Fetches the SARIF rendering of the same submission (a second, format=sarif request). */
  onRequestSarif: () => Promise<unknown>;
}

export function ReportView({ report, onRequestSarif }: ReportViewProps) {
  const name = report.artifact_meta.name;
  const scope = report.artifact_meta.scope;

  async function downloadSarif() {
    const sarif = await onRequestSarif();
    downloadBlob("scan.sarif.json", JSON.stringify(sarif, null, 2), "application/sarif+json");
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <KindBadge kind={report.artifact_meta.kind} />
        {/* untrusted artifact name / scope → inert escaped text */}
        {name ? <span className="font-mono text-sm text-ink">{name}</span> : null}
        {scope ? <span className="font-mono text-xs text-faint">scope: {scope}</span> : null}
        <div className="ml-auto flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              downloadBlob("scan.json", JSON.stringify(report, null, 2), "application/json")
            }
          >
            <Download /> JSON
          </Button>
          <Button variant="outline" size="sm" onClick={downloadSarif}>
            <Download /> SARIF
          </Button>
        </div>
      </div>

      <VerdictBanner report={report} />

      {/* "judges used" transparency line */}
      <div className="flex items-center gap-2 font-mono text-[11px] text-faint">
        <Gavel className="size-3.5" aria-hidden />
        {report.judges_used.length > 0 ? (
          <span>judges used: {report.judges_used.join(", ")}</span>
        ) : (
          <span>judges used: none (deterministic static analysis only)</span>
        )}
      </div>

      <FindingsList findings={report.findings} />
      <ImportsList imports={report.imports} />
      <ComponentsTable components={report.components} />
    </div>
  );
}
