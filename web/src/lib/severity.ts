import type { Severity, Verdict } from "./api/client";

/** Severity badge tone keys (match the Badge component's `tone` variants). */
export type SeverityTone = "critical" | "high" | "medium" | "low" | "info";

/** Highest-to-lowest, so findings render with the scariest first. */
export const SEVERITY_ORDER: Severity[] = ["critical", "high", "medium", "low", "info"];

export function severityTone(severity: Severity): SeverityTone {
  return severity as SeverityTone;
}

export interface VerdictStyle {
  label: string;
  /** CSS var color used for the banner accents. */
  color: string;
  blurb: string;
}

export const VERDICT_STYLE: Record<Verdict, VerdictStyle> = {
  CLEAN: {
    label: "Clean",
    color: "var(--color-clean)",
    blurb: "No blocking findings. Safe to install with normal review.",
  },
  CAUTION: {
    label: "Caution",
    color: "var(--color-caution)",
    blurb: "Suspicious patterns found. Review the findings before installing.",
  },
  DO_NOT_INSTALL: {
    label: "Do Not Install",
    color: "var(--color-danger)",
    blurb: "Critical risk detected. Do not install this artifact.",
  },
};
