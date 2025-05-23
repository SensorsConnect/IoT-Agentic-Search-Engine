const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  sassOptions: {
    // includePaths: [path.join(__dirname, 'styles')]
  },
  reactStrictMode: false,
  logging: {
    fetches: {
      fullUrl: true
    }
  },
  async redirects() {
    return [
      {
        source: '/IoT-ASE-Demo/chat',
        destination: '/',
        permanent: true, // Use false if this is a temporary redirect
      },
    ];
  }
};

module.exports = nextConfig;
