import { CheckCircle2, ShieldAlert, ShieldX } from "lucide-react";

import type { ScanReport } from "@/lib/api/client";
import { VERDICT_STYLE } from "@/lib/severity";

const VERDICT_ICON = {
  CLEAN: CheckCircle2,
  CAUTION: ShieldAlert,
  DO_NOT_INSTALL: ShieldX,
} as const;

/** The headline verdict + risk score banner. */
export function VerdictBanner({ report }: { report: ScanReport }) {
  const style = VERDICT_STYLE[report.verdict];
  const Icon = VERDICT_ICON[report.verdict];
  const score = report.score;

  return (
    <div
      className="relative overflow-hidden rounded-lg border p-6"
      style={{
        borderColor: `color-mix(in srgb, ${style.color} 45%, transparent)`,
        background: `linear-gradient(180deg, color-mix(in srgb, ${style.color} 12%, transparent), transparent 70%)`,
      }}
    >
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div className="flex items-start gap-4">
          <Icon className="mt-0.5 size-9 shrink-0" style={{ color: style.color }} aria-hidden />
          <div>
            <div
              className="font-mono text-2xl font-bold uppercase tracking-tight"
              style={{ color: style.color }}
            >
              {style.label}
            </div>
            <p className="mt-1 max-w-md text-sm text-muted">{style.blurb}</p>
          </div>
        </div>

        <div className="text-right">
          <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-faint">
            Risk score
          </div>
          <div className="font-mono text-4xl font-bold tabular-nums" style={{ color: style.color }}>
            {score}
            <span className="text-lg text-faint">/100</span>
          </div>
        </div>
      </div>

      <div className="mt-5 h-1.5 w-full overflow-hidden rounded-full bg-canvas/80">
        <div
          className="h-full rounded-full transition-[width] duration-700"
          style={{ width: `${Math.min(100, Math.max(0, score))}%`, backgroundColor: style.color }}
        />
      </div>

      {report.summary ? <p className="mt-4 text-sm leading-relaxed text-ink/90">{report.summary}</p> : null}
    </div>
  );
}
