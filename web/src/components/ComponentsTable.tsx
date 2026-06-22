import { Check, Minus } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Component } from "@/lib/api/client";

/** The component inventory: every file the engine discovered and how it classified it. */
export function ComponentsTable({ components }: { components: Component[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Components · {components.length}</CardTitle>
      </CardHeader>
      <CardContent>
        {components.length === 0 ? (
          <p className="text-sm text-faint">No components discovered.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-line text-left font-mono text-[11px] uppercase tracking-wider text-faint">
                  <th className="py-2 pr-4 font-medium">Path</th>
                  <th className="py-2 pr-4 font-medium">Type</th>
                  <th className="py-2 pr-4 font-medium">Language</th>
                  <th className="py-2 font-medium">Executable</th>
                </tr>
              </thead>
              <tbody>
                {components.map((c, i) => (
                  <tr key={`${c.path}-${i}`} className="border-b border-line/50 last:border-0">
                    {/* untrusted path → inert escaped text */}
                    <td className="py-2 pr-4 font-mono text-[13px] text-ink">{c.path}</td>
                    <td className="py-2 pr-4">
                      <Badge tone="neutral">{c.type}</Badge>
                    </td>
                    <td className="py-2 pr-4 font-mono text-xs text-muted">{c.language ?? "—"}</td>
                    <td className="py-2">
                      {c.executable ? (
                        <span className="inline-flex items-center gap-1 font-mono text-xs text-sev-high">
                          <Check className="size-3.5" aria-hidden /> yes
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 font-mono text-xs text-faint">
                          <Minus className="size-3.5" aria-hidden /> no
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
