import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded border px-2 py-0.5 font-mono text-[11px] font-semibold uppercase tracking-wider",
  {
    variants: {
      tone: {
        neutral: "border-line-bright bg-panel-2 text-muted",
        scan: "border-scan/40 bg-scan/10 text-scan",
        critical: "border-sev-critical/40 bg-sev-critical/12 text-sev-critical",
        high: "border-sev-high/40 bg-sev-high/12 text-sev-high",
        medium: "border-sev-medium/40 bg-sev-medium/12 text-sev-medium",
        low: "border-sev-low/40 bg-sev-low/12 text-sev-low",
        info: "border-sev-info/40 bg-sev-info/12 text-sev-info",
      },
    },
    defaultVariants: { tone: "neutral" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, tone, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ tone }), className)} {...props} />;
}

export { badgeVariants };
