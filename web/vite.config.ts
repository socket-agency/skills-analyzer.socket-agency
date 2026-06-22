/// <reference types="vitest/config" />
import path from "node:path";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// The `@/` alias must be configured in BOTH this file and tsconfig.json, or component
// imports resolve in the editor but break at build time (a documented shadcn gotcha).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(import.meta.dirname, "./src") },
  },
  // In dev, proxy API calls to the FastAPI backend so the SPA and API share an origin
  // (mirrors production, where FastAPI serves both the static bundle and /scan).
  server: {
    proxy: {
      "/scan": "http://localhost:8000",
      "/api": "http://localhost:8000",
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    css: false,
  },
});
