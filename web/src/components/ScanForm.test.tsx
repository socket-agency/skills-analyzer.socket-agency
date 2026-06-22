import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ScanForm } from "@/components/ScanForm";

describe("ScanForm demo examples", () => {
  it("loads a malicious example into the textarea on click", async () => {
    const user = userEvent.setup();
    render(<ScanForm busy={false} onSubmit={vi.fn()} />);

    const textarea = screen.getByLabelText("Artifact content") as HTMLTextAreaElement;
    expect(textarea.value).toBe("");

    await user.click(screen.getByRole("button", { name: /Reverse-shell skill/ }));

    expect(textarea.value).toContain("socat tcp:evil.example");
    expect(textarea.value).toContain("allowed-tools: Bash(*)");
  });

  it("submits the loaded example as a text-mode FormData", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ScanForm busy={false} onSubmit={onSubmit} />);

    await user.click(screen.getByRole("button", { name: /Clean skill/ }));
    await user.click(screen.getByRole("button", { name: /Run scan/ }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const form = onSubmit.mock.calls[0][0] as FormData;
    expect(form.get("mode")).toBe("text");
    expect(form.get("kind_hint")).toBe("skill");
    expect(String(form.get("content"))).toContain("read-only helper");
  });
});
