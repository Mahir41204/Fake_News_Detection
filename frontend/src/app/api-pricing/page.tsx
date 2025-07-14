"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface ApiTier {
  name: string;
  price: string;
  rate_limit: string;
  daily_limit: string;
  features: string[];
}

interface ApiTiers {
  [key: string]: ApiTier;
}

// Update planIcons for dark mode (use bright emojis for now)
const planIcons: Record<string, React.ReactNode> = {
  free: <span className="text-5xl text-blue-400">🟦</span>,
  basic: <span className="text-5xl text-blue-400">🟩</span>,
  pro: <span className="text-5xl text-blue-400">🟨</span>,
  enterprise: <span className="text-5xl text-blue-400">🟪</span>,
};

// Add descriptions for each plan
const planDescriptions: Record<string, string> = {
  free: 'Best for testing and personal use. Basic analysis and limited requests.',
  basic: 'For small projects and startups. Includes language analysis and red flag detection.',
  pro: 'For growing teams and businesses. Adds source credibility and educational content.',
  enterprise: 'Custom solutions for large organizations. Enhanced analysis and support.',
};

export default function ApiPricingPage() {
  const [tiers, setTiers] = useState<ApiTiers>({});
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetch('/api/keys')
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        setTiers(data.tiers);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load API tiers:', err);
        setLoading(false);
        // Set default tiers if API fails
        setTiers({
          free: {
            name: "Free",
            price: "$0/month",
            rate_limit: "10 requests/minute",
            daily_limit: "100 requests/day",
            features: [
              "Basic misinformation analysis",
              "Credibility scoring",
              "Verdict classification",
            ],
          },
          basic: {
            name: "Basic",
            price: "$29/month",
            rate_limit: "50 requests/minute",
            daily_limit: "1,000 requests/day",
            features: [
              "All Free features",
              "Language pattern analysis",
              "Red flag detection",
            ],
          },
          pro: {
            name: "Professional",
            price: "$99/month",
            rate_limit: "200 requests/minute",
            daily_limit: "10,000 requests/day",
            features: [
              "All Basic features",
              "Source credibility analysis",
              "Educational content",
              "Priority support",
            ],
          },
          enterprise: {
            name: "Enterprise",
            price: "Custom pricing",
            rate_limit: "1,000 requests/minute",
            daily_limit: "100,000 requests/day",
            features: [
              "All Pro features",
              "Enhanced evidence analysis",
              "Custom integrations",
              "Dedicated support",
            ],
          },
        });
      });
  }, []);

  const handleDemoRedirect = (plan: string) => {
    // For demo purposes, just show an alert
    alert(`Demo mode: ${plan} plan selected. In a real application, this would redirect to signup.`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#fcfbf9]">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-800">🔍 MisinfoDetector</h1>
            </div>
            <div className="flex items-center space-x-6">
              <a href="/" className="text-gray-600 hover:text-gray-800 font-medium">
                Home
              </a>
              <a href="/api-pricing" className="text-blue-600 font-medium">
                Pricing
              </a>
              <a href="/docs" className="text-gray-600 hover:text-gray-800 font-medium">
                API Docs
              </a>
              <a 
                href="/" 
                className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Try Demo
              </a>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex flex-col md:flex-row">
        {/* Left column: Heading and subtitle */}
        <div className="md:w-1/2 flex flex-col justify-center px-12 py-20 md:py-0">
          <h1 className="text-6xl font-extrabold text-blue-600 mb-4 leading-tight">Our Services</h1>
          <p className="text-xl text-blue-500 mb-8">Let's grow your business together.</p>
          <div className="hidden md:block w-full h-0.5 bg-blue-500 my-8" />
        </div>
        {/* Right column: Pricing cards */}
        <div className="md:w-1/2 flex flex-col justify-center px-4 md:px-0">
          <div className="w-full max-w-2xl mx-auto space-y-10">
            <div className="block md:hidden w-full h-0.5 bg-blue-500 my-8" />
            {Object.entries(tiers).map(([key, tier]) => (
              <div
                key={key}
                className="flex flex-row items-center justify-between border-t border-b border-blue-400 py-8 px-6 bg-white rounded-lg shadow-sm space-x-8"
              >
                <div className="flex-shrink-0">{planIcons[key] || <span className='text-5xl text-blue-400'>💠</span>}</div>
                <div className="flex-1 min-w-0 ml-6">
                  <div className="font-extrabold text-blue-600 text-xl mb-1">{tier.name}</div>
                  <div className="text-blue-500 text-md mb-1">{planDescriptions[key]}</div>
                  <div className="text-blue-400 text-sm mb-2">{tier.rate_limit} &bull; {tier.daily_limit}</div>
                  <ul className="list-disc list-inside text-blue-400 text-sm space-y-1">
                    {tier.features.map((feature, idx) => (
                      <li key={idx}>{feature}</li>
                    ))}
                  </ul>
                </div>
                <div className="flex flex-col items-end space-y-3 min-w-[120px] ml-6">
                  <div className="text-blue-600 font-bold text-xl">{tier.price}</div>
                  {(key === 'free' || key === 'pro' || key === 'basic') && (
                    <button
                      className="border-2 border-blue-600 text-blue-600 px-7 py-2 rounded-full font-semibold hover:bg-blue-600 hover:text-white transition-all duration-150 text-lg"
                      onClick={() => handleDemoRedirect(key)}
                    >
                      {key === 'free' ? 'Try Demo' : 'Try Demo'}
                    </button>
                  )}
                  {key === 'enterprise' && (
                    <a href="/contact" className="border-2 border-blue-600 text-blue-600 px-7 py-2 rounded-full font-semibold hover:bg-blue-600 hover:text-white transition-all duration-150 text-lg text-center">
                      Contact Sales
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 