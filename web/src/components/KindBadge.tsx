import { FileCode2, FileText, ScrollText } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { ArtifactKind } from "@/lib/api/client";

const KIND_META: Record<ArtifactKind, { label: string; Icon: typeof FileCode2 }> = {
  skill: { label: "SKILL.md", Icon: FileCode2 },
  agents: { label: "AGENTS.md", Icon: ScrollText },
  claude_md: { label: "CLAUDE.md", Icon: FileText },
};

/** The artifact-kind badge — which analysis profile the engine applied. */
export function KindBadge({ kind }: { kind: ArtifactKind }) {
  const { label, Icon } = KIND_META[kind];
  return (
    <Badge tone="scan">
      <Icon aria-hidden /> {label}
    </Badge>
  );
}
