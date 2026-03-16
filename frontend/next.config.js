/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: false,
  logging: {
    fetches: {
      fullUrl: true
    }
  },
};

module.exports = nextConfig;
