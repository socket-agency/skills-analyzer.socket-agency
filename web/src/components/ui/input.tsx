import * as React from "react";

import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input
      ref={ref}
      type={type}
      className={cn(
        "flex h-10 w-full rounded-md border border-line bg-canvas/70 px-3 py-2 font-mono text-[13px] text-ink placeholder:text-faint transition-colors file:mr-3 file:rounded file:border-0 file:bg-panel-2 file:px-2 file:py-1 file:font-mono file:text-xs file:text-muted focus-visible:border-scan/50 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-scan/40",
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = "Input";
