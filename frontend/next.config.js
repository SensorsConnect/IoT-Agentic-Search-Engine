/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: false,
  logging: {
    fetches: {
      fullUrl: true
    }
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        // Use 127.0.0.1 explicitly: on Node 18+, `localhost` resolves to ::1 (IPv6)
        // first, but uvicorn's --host 0.0.0.0 binds IPv4 only -> ECONNREFUSED ::1:8000.
        destination: `${process.env.BACKEND_DEV_URL || 'http://127.0.0.1:8000'}/api/v1/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'geolocation=(self)',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
