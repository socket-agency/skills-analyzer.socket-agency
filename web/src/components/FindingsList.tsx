import { MapPin } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Finding } from "@/lib/api/client";
import { SEVERITY_ORDER, severityTone } from "@/lib/severity";

function FindingRow({ finding }: { finding: Finding }) {
  const loc = finding.location.line
    ? `${finding.location.file}:${finding.location.line}`
    : finding.location.file;
  return (
    <div className="rounded-md border border-line/70 bg-canvas/40 p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={severityTone(finding.severity)}>{finding.severity}</Badge>
        <span className="font-mono text-[13px] font-semibold text-ink">
          {finding.category.replace(/_/g, " ")}
        </span>
        <span className="font-mono text-[11px] text-faint">conf: {finding.confidence}</span>
        <span className="ml-auto font-mono text-[11px] text-faint">{finding.id}</span>
      </div>

      <div className="mt-2 flex items-center gap-1.5 font-mono text-xs text-muted">
        <MapPin className="size-3.5 shrink-0" aria-hidden />
        {/* untrusted location → inert escaped text */}
        <span className="break-all">{loc}</span>
      </div>

      {/* Evidence is attacker-controlled. Rendered as inert, escaped, monospace text:
          no markdown, no HTML, no auto-linking. */}
      <pre className="mt-3 overflow-x-auto rounded border border-line bg-canvas/80 p-3 font-mono text-[12px] leading-relaxed text-ink/90">
        <code>{finding.evidence}</code>
      </pre>

      <dl className="mt-3 space-y-2 text-sm">
        <div>
          <dt className="font-mono text-[11px] uppercase tracking-wider text-faint">Risk</dt>
          <dd className="text-ink/90">{finding.risk}</dd>
        </div>
        <div>
          <dt className="font-mono text-[11px] uppercase tracking-wider text-faint">Remediation</dt>
          <dd className="text-ink/90">{finding.remediation}</dd>
        </div>
      </dl>

      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[11px] text-faint">
        <span>layer: {finding.source_layer}</span>
        {finding.language ? <span>· lang: {finding.language}</span> : null}
        {finding.raised_by ? <span>· judge: {finding.raised_by}</span> : null}
      </div>
    </div>
  );
}

/** All findings, grouped severity-first (critical → info). */
export function FindingsList({ findings }: { findings: Finding[] }) {
  const groups = SEVERITY_ORDER.map((sev) => ({
    severity: sev,
    items: findings.filter((f) => f.severity === sev),
  })).filter((g) => g.items.length > 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Findings · {findings.length}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {findings.length === 0 ? (
          <p className="text-sm text-faint">No findings. The artifact looks clean.</p>
        ) : (
          groups.map((g) => (
            <section key={g.severity} className="space-y-3">
              <h4 className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.16em] text-faint">
                <Badge tone={severityTone(g.severity)}>{g.severity}</Badge>
                <span>· {g.items.length}</span>
              </h4>
              <div className="space-y-3">
                {g.items.map((f, i) => (
                  <FindingRow key={`${f.id}-${i}`} finding={f} />
                ))}
              </div>
            </section>
          ))
        )}
      </CardContent>
    </Card>
  );
}
