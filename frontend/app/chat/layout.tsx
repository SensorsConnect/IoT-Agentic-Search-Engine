import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Chat - AI Local Search',
  description:
    'Chat with Localelive AI to find nearby services, restaurants, shops, and more. Get personalized local recommendations in real time.',
  openGraph: {
    title: 'Chat - AI Local Search | Localelive',
    description:
      'Chat with Localelive AI to find nearby services, restaurants, shops, and more. Get personalized local recommendations in real time.',
    url: 'https://localelive.space/chat',
    type: 'website',
  },
  alternates: {
    canonical: 'https://localelive.space/chat',
  },
}

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
