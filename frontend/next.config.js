require('path')

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
  }
}

module.exports = nextConfig
