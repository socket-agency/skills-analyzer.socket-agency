import * as React from "react";

import { cn } from "@/lib/utils";

export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "flex min-h-[15rem] w-full resize-y rounded-md border border-line bg-canvas/70 px-3 py-2.5 font-mono text-[13px] leading-relaxed text-ink placeholder:text-faint transition-colors focus-visible:border-scan/50 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-scan/40",
      className,
    )}
    {...props}
  />
));
Textarea.displayName = "Textarea";
