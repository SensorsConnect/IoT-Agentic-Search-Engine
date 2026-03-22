import Image from 'next/image';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Logo Section */}
      <div className="container mx-auto px-4 pt-8">
        <div className="flex justify-center">
          <div className="relative size-48">
            <Image
              src="/localelive-light-icon.png"
              alt="localelive"
              fill
              className="object-contain dark:hidden"
              priority
            />
            <Image
              src="/localelive-dark-icon.png"
              alt="localelive"
              fill
              className="object-contain hidden dark:block"
              priority
            />
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
          🌍 Welcome to Localelive
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          The pulse of places lives at your fingertips.
          </p>
          <Link
            href="/chat"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 dark:text-white">📍 Personalized Location Feeds</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Get tailored information based on your interests and your surroundings.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 dark:text-white">🔍 Explore with Confidence</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Make better decisions before stepping out. From hidden gems to popular spots, LocaleLive gives you the full picture.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 dark:text-white">🚦 Crowd Dynamics & Foot Traffic</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Know when a place is buzzing or when it&apos;s the perfect time to visit.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 dark:text-white">🧠 Smart Alerts</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Receive intelligent notifications about places you follow — from traffic to sudden events.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 dark:text-white">🤝 Community-Powered Updates</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Hear directly from locals. Share experiences, tips, and updates about places in your neighborhood.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 dark:text-white">✅ Live Local Insights</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Stay updated with the latest events, activities, and trends in your area — as they happen.
            </p>
          </div>
        </div>
      </div>

      {/* Example Section */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-6 text-center dark:text-white">Real-Time Recommendations</h3>
            <div className="space-y-4">
              <div className="flex justify-end">
                <div className="bg-blue-600 text-white rounded-2xl rounded-tr-none px-4 py-2 max-w-[80%]">
                  <p>I&apos;m not feeling well, and I&apos;m looking for a walk-in clinic</p>
                </div>
              </div>
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-tl-none px-4 py-2 max-w-[80%]">
                  <p>I recommend St. Clair Medical Clinic (4.2★) at 1849 Yonge St. It&apos;s nearby with a 20-minute wait time. Would you like directions?</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-6 text-center dark:text-white">Personalized Suggestions</h3>
            <div className="space-y-4">
              <div className="flex justify-end">
                <div className="bg-blue-600 text-white rounded-2xl rounded-tr-none px-4 py-2 max-w-[80%]">
                  <p>I want to find a restaurant that&apos;s not too crowded and has outdoor seating</p>
                </div>
              </div>
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-tl-none px-4 py-2 max-w-[80%]">
                  <p>&quot;Garden Bistro&quot; has 3 outdoor tables available right now, and the current wait time is only 5 minutes. They&apos;re known for their fresh local ingredients. Would you like to see the menu?</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 max-w-3xl mx-auto">
          <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-center dark:text-white">Smart Features</h3>
            <p className="text-gray-600 dark:text-gray-300 text-center">
              🧠 Our AI assistant continuously learns from your preferences and combines them with real-time data to provide the most relevant recommendations for your current needs.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-4 py-16">
      <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md max-w-4xl mx-auto text-center">
        {/* <div className="bg-white dark:bg-gray-800 rounded-lg p-12 text-center"> */}
          <h2 className="text-3xl font-bold text-gray-800  dark:text-white mb-6">
            🚀 Ready to Experience LocaleLive?
          </h2>
          <p className="text-xl text-gray-900 dark:text-gray-300 mb-8">
            Start exploring and discover real-time insights about places around you — from crowd levels to personalized recommendations.
          </p>
          <Link
            href="/chat"
            className="inline-block bg-blue-600 text-white  dark:text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700  dark:hover:bg-gray-600 transition-colors"
          >
            Start Exploring
          </Link>
        </div>
      </div>

      {/* Contact Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">
            📬 Contact Us
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-4">
            Have questions about LocaleLive? We'd love to hear from you!
          </p>
          <div className="flex items-center justify-center space-x-2">
            <svg className="size-6 text-blue-600  dark:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <a href="mailto:info@localelive.space" className="text-blue-600 dark:text-white hover:underline text-xl">
              info@localelive.space
            </a>
          </div>
        </div>
      </div>

      {/* Footer Section */}
      <footer className="bg-gray-100 dark:bg-gray-900 py-12 mt-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {/* Left side - Demo Info */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">About LocaleLive</h3>
              <p className="text-gray-600 dark:text-gray-300">
                LocaleLive is an AI-powered platform that helps you discover nearby services and places with real-time insights and personalized recommendations.
              </p>
            </div>
            
            {/* Right side - Quick Links */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Quick Links</h3>
              <div className="flex flex-col space-y-4">
                <a
                  href="/chat"
                  className="text-blue-600 dark:text-white hover:underline flex items-center"
                >
                  Start Exploring
                </a>
                <a
                  href="mailto:info@localelive.space"
                  className="text-blue-600 dark:text-white hover:underline flex items-center"
                >
                  Contact Us
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
} 