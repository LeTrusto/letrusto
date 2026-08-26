import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      { source: "/ai", destination: "/shop", permanent: true },
      { source: "/ai-tools", destination: "/shop", permanent: true },
      { source: "/ai-tools/:path*", destination: "/shop", permanent: true },
      { source: "/compare", destination: "/shop", permanent: true },
      { source: "/guides", destination: "/shop", permanent: true },
      { source: "/guides/:path*", destination: "/shop", permanent: true },
      { source: "/articles", destination: "/shop", permanent: true },
      { source: "/articles/:path*", destination: "/shop", permanent: true },
      { source: "/category/:path*", destination: "/shop", permanent: true },
      { source: "/categories", destination: "/shop", permanent: true },
      { source: "/search", destination: "/shop", permanent: true },
      { source: "/methodology", destination: "/how-it-works", permanent: true },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "source.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "upload.wikimedia.org",
      },
      {
        protocol: "https",
        hostname: "cf.cjdropshipping.com",
      },
      {
        protocol: "https",
        hostname: "oss-cf.cjdropshipping.com",
      },
    ],
  },
};

export default nextConfig;
