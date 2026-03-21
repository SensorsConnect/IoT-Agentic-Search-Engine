import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/sign-in', '/sign-up', '/api/'],
      },
    ],
    sitemap: 'https://localelive.space/sitemap.xml',
  }
}
