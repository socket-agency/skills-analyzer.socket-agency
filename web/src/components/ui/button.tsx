import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium font-mono tracking-tight transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-scan/60 disabled:pointer-events-none disabled:opacity-50 [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        primary:
          "bg-scan text-canvas font-semibold hover:bg-scan/90 shadow-[0_0_0_1px_rgba(52,224,161,0.4),0_8px_24px_-12px_rgba(52,224,161,0.5)]",
        outline:
          "border border-line-bright bg-panel-2/40 text-ink hover:bg-panel-2 hover:border-scan/50",
        ghost: "text-muted hover:text-ink hover:bg-panel-2/60",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 px-3 text-xs",
        lg: "h-12 px-6 text-base",
      },
    },
    defaultVariants: { variant: "primary", size: "default" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  ),
);
Button.displayName = "Button";

export { buttonVariants };
