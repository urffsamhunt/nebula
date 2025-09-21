import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Prevent Next.js from running ESLint during `next build`.
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Prevent Next.js from failing the build on TypeScript type errors.
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
