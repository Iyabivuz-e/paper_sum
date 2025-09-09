import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: false,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  // Fix for deployment routing issues
  trailingSlash: false,
  // Optimize for production
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
};

export default nextConfig;
