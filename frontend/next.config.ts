import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Two lockfiles exist in this repo (root = deck tooling, frontend = app).
  // Pin the workspace root so Next/Turbopack never infers the wrong one.
  turbopack: {
    root: path.join(__dirname),
  },
  // Emit a self-contained server bundle (.next/standalone/server.js) so the
  // Docker image is tiny and the Cloud Run deploy is deterministic — no reliance
  // on buildpack auto-detection. Local `next dev` / `next start` are unaffected.
  output: "standalone",
};

export default nextConfig;
