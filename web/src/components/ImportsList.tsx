import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ImportRef } from "@/lib/api/client";

const KIND_TONE = {
  in_tree: "neutral",
  out_of_tree: "high",
  remote: "critical",
} as const;

/** Resolved CLAUDE.md `@import` targets — out-of-tree / remote imports are poisoning vectors. */
export function ImportsList({ imports }: { imports: ImportRef[] }) {
  if (imports.length === 0) return null;
  return (
    <Card>
      <CardHeader>
        <CardTitle>Imports · {imports.length}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {imports.map((imp, i) => (
          <div
            key={`${imp.raw}-${i}`}
            className="flex flex-wrap items-center gap-2 rounded border border-line/70 bg-canvas/40 px-3 py-2"
          >
            <Badge tone={KIND_TONE[imp.kind]}>{imp.kind.replace("_", " ")}</Badge>
            {/* untrusted import target → inert escaped text, never an anchor */}
            <code className="font-mono text-[13px] text-ink">{imp.target}</code>
            {imp.resolved ? (
              <span className="font-mono text-[11px] text-scan">resolved</span>
            ) : (
              <span className="font-mono text-[11px] text-faint">unresolved</span>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
