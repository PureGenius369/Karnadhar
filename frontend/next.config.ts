import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Two lockfiles exist in this repo (root = deck tooling, frontend = app).
  // Pin the workspace root so Next/Turbopack never infers the wrong one.
  turbopack: {
    root: path.join(__dirname),
  },
};

export default nextConfig;
