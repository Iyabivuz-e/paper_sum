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
  // Enhanced webpack configuration for Vercel compatibility
  webpack: (config, { dev, isServer }) => {
    // Explicit alias configuration for production builds
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.join(__dirname, 'src'),
      '@/components': path.join(__dirname, 'src', 'components'),
      '@/lib': path.join(__dirname, 'src', 'lib'),
      '@/utils': path.join(__dirname, 'src', 'utils'),
    };
    
    // Ensure proper module resolution for production
    config.resolve.modules = [
      path.join(__dirname, 'src'),
      'node_modules'
    ];
    
    return config;
  },
};

export default nextConfig;
