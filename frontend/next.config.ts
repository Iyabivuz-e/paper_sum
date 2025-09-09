import type { NextConfig } from "next";
import path from "path";

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
  // Fix workspace root detection
  outputFileTracingRoot: __dirname,
  // Explicit webpack configuration for path resolution
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
    };
    return config;
  },
};

export default nextConfig;
