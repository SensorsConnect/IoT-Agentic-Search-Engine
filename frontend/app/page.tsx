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
              alt="IoT-ASE Logo"
              fill
              className="object-contain dark:hidden"
              priority
            />
            <Image
              src="/localelive-dark-icon.png"
              alt="IoT-ASE Logo"
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
            Try Demo
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
            Try our demo now and discover real-time insights about places around you - from crowd levels to personalized recommendations.
          </p>
          <Link
            href="/chat"
            className="inline-block bg-blue-600 text-white  dark:text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            Launch Demo
          </Link>
        </div>
      </div>

      {/* Footer Section */}
      <footer className="bg-gray-100 dark:bg-gray-900 py-12 mt-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {/* Left side - Demo Info */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">About This Demo</h3>
              <p className="text-gray-600 dark:text-gray-300">
                This is a demonstration of the Agentic Search Engine paper implementation. The default location is set to Toronto, Canada.
              </p>
              <p className="text-gray-600 dark:text-gray-300">
                To get recommendations, please specify your location (e.g., Ottawa, Montreal, Oshawa, etc.).
              </p>
            </div>
            
            {/* Right side - Links and Logos */}
            <div className="space-y-8">
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Resources</h3>
                <div className="flex flex-col space-y-4">
                  <a 
                    href="https://github.com/SensorsConnect/IoT-Agentic-Search-Engine" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-white hover:underline flex items-center"
                  >
                    <svg className="size-6 mr-2" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                    </svg>
                    GitHub Repository
                  </a>
                  <a 
                    href="https://arxiv.org/abs/2503.12255" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-white hover:underline flex items-center"
                  >
                    <svg className="size-6 mr-2" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
                      <path d="M7 7h10v2H7zm0 4h10v2H7zm0 4h7v2H7z"/>
                    </svg>
                    Research Paper
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
} 