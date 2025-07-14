'use client';

export default function ApiDocsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            API Documentation
          </h1>
          <p className="text-xl text-gray-600">
            Integrate misinformation detection into your applications with our powerful API
          </p>
        </div>

        {/* Quick Start */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">🚀 Quick Start</h2>
          
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">1. Try the Demo</h3>
              <p className="text-gray-600 mb-3">
                Experience our misinformation detection system with the interactive demo. No signup required.
              </p>
              <a
                href="/"
                className="inline-block bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Try Demo
              </a>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">2. Make Your First Request</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{`curl -X POST "http://localhost:8000/analyze" \\
  -H "Authorization: Bearer demo_key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "source_text": "Your text to analyze here"
  }'`}</pre>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">3. Handle the Response</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{`{
  "analyzed_claim": "The main claim extracted from the text",
  "credibility_score": 75,
  "verdict": "SUPPORTED",
  "confidence": 85,
  "tier": "pro",
  "analysis_method": "FEVER_evidence_corpus",
  "language_analysis": {
    "emotional_language": 2,
    "certainty_indicators": 1,
    "urgency_indicators": 0,
    "conspiracy_indicators": 0,
    "red_flags": []
  },
  "source_analysis": {
    "reputation_score": 85,
    "trust_indicators": ["Secure connection (HTTPS)"],
    "warning_signs": []
  },
  "educational_content": {
    "tips": ["Always verify claims with multiple sources"],
    "why_this_matters": "Accurate information is crucial...",
    "how_to_spot_similar": ["Watch for excessive emotional language"]
  },
  "analysis_timestamp": "2024-01-15T10:30:00Z"
}`}</pre>
              </div>
            </div>
          </div>
        </div>

        {/* API Endpoints */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">📡 API Endpoints</h2>
          
          <div className="space-y-8">
            {/* Analyze Endpoint */}
            <div className="border-b border-gray-200 pb-6">
              <div className="flex items-center mb-4">
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold mr-3">
                  POST
                </span>
                <h3 className="text-xl font-semibold text-gray-800">/analyze</h3>
              </div>
              
              <p className="text-gray-600 mb-4">
                Analyze text or URL content for misinformation. Returns credibility score, verdict, and detailed analysis.
              </p>
              
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <h4 className="font-semibold text-gray-700 mb-2">Request Body:</h4>
                <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm">
                  <pre>{`{
  "source_text": "string (required)",
  "source_url": "string (optional)"
}`}</pre>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-2">Response Fields:</h4>
                <div className="space-y-2 text-sm">
                  <div><span className="font-semibold">analyzed_claim:</span> The main claim extracted from the text</div>
                  <div><span className="font-semibold">credibility_score:</span> Score from 0-100 indicating credibility</div>
                  <div><span className="font-semibold">verdict:</span> SUPPORTED, REFUTED, or NEUTRAL</div>
                  <div><span className="font-semibold">confidence:</span> Confidence level of the analysis (0-100)</div>
                  <div><span className="font-semibold">tier:</span> Your current API tier</div>
                  <div><span className="font-semibold">language_analysis:</span> Available on Basic+ tiers</div>
                  <div><span className="font-semibold">source_analysis:</span> Available on Pro+ tiers</div>
                  <div><span className="font-semibold">educational_content:</span> Available on Pro+ tiers</div>
                </div>
              </div>
            </div>

            {/* Usage Stats Endpoint */}
            <div className="border-b border-gray-200 pb-6">
              <div className="flex items-center mb-4">
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold mr-3">
                  GET
                </span>
                <h3 className="text-xl font-semibold text-gray-800">/api/usage</h3>
              </div>
              
              <p className="text-gray-600 mb-4">
                Get your current API usage statistics and remaining limits.
              </p>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-2">Response:</h4>
                <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm">
                  <pre>{`{
  "tier": "pro",
  "rate_limit": 200,
  "daily_limit": 10000,
  "current_usage": {
    "requests_this_minute": 5,
    "requests_today": 150,
    "remaining_today": 9850
  }
}`}</pre>
                </div>
              </div>
            </div>

            {/* Health Check Endpoint */}
            <div>
              <div className="flex items-center mb-4">
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold mr-3">
                  GET
                </span>
                <h3 className="text-xl font-semibold text-gray-800">/api/health</h3>
              </div>
              
              <p className="text-gray-600 mb-4">
                Check the health status of the API and its services.
              </p>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-2">Response:</h4>
                <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm">
                  <pre>{`{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "fever_corpus": "operational",
    "claim_classifier": "operational",
    "claim_extractor": "operational"
  }
}`}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Code Examples */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">💻 Code Examples</h2>
          
          <div className="space-y-6">
            {/* Python Example */}
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-3">Python</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{`import requests

def analyze_misinformation(text):
    url = "http://localhost:8000/analyze"
    headers = {
        "Authorization": "Bearer demo_key",
        "Content-Type": "application/json"
    }
    data = {"source_text": text}
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Usage
result = analyze_misinformation("Your text to analyze here")
print(f"Credibility Score: {result['credibility_score']}")
print(f"Verdict: {result['verdict']}")`}</pre>
              </div>
            </div>

            {/* JavaScript Example */}
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-3">JavaScript</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{`async function analyzeMisinformation(text) {
    const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer demo_key',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ source_text: text })
    });
    
    return await response.json();
}

// Usage
const result = await analyzeMisinformation(
    'Your text to analyze here',
    'your_api_key_here'
);
console.log(\`Credibility Score: \${result.credibility_score}\`);
console.log(\`Verdict: \${result.verdict}\`);`}</pre>
              </div>
            </div>

            {/* Node.js Example */}
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-3">Node.js</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{`const axios = require('axios');

async function analyzeMisinformation(text, apiKey) {
    try {
        const response = await axios.post('https://api.misinfodetector.com/analyze', {
            source_text: text
        }, {
            headers: {
                'Authorization': \`Bearer \${apiKey}\`,
                'Content-Type': 'application/json'
            }
        });
        
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
        throw error;
    }
}

// Usage
analyzeMisinformation('Your text to analyze here', 'your_api_key_here')
    .then(result => {
        console.log(\`Credibility Score: \${result.credibility_score}\`);
        console.log(\`Verdict: \${result.verdict}\`);
    })
    .catch(error => {
        console.error('Analysis failed:', error);
    });`}</pre>
              </div>
            </div>
          </div>
        </div>

        {/* Error Handling */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">⚠️ Error Handling</h2>
          
          <div className="space-y-4">
            <div className="border-l-4 border-red-500 pl-4">
              <h3 className="font-semibold text-red-700">401 Unauthorized</h3>
              <p className="text-gray-600">Invalid or missing API key</p>
              <div className="bg-gray-900 text-red-400 p-3 rounded font-mono text-sm mt-2">
                <pre>{`{"detail": "Invalid API key"}`}</pre>
              </div>
            </div>
            
            <div className="border-l-4 border-orange-500 pl-4">
              <h3 className="font-semibold text-orange-700">429 Too Many Requests</h3>
              <p className="text-gray-600">Rate limit or daily limit exceeded</p>
              <div className="bg-gray-900 text-orange-400 p-3 rounded font-mono text-sm mt-2">
                <pre>{`{"detail": "Rate limit exceeded"}`}</pre>
              </div>
            </div>
            
            <div className="border-l-4 border-red-500 pl-4">
              <h3 className="font-semibold text-red-700">400 Bad Request</h3>
              <p className="text-gray-600">Invalid request format or missing required fields</p>
              <div className="bg-gray-900 text-red-400 p-3 rounded font-mono text-sm mt-2">
                <pre>{`{"detail": "Input text is empty"}`}</pre>
              </div>
            </div>
          </div>
        </div>

        {/* Rate Limits */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">📊 Rate Limits</h2>
          
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gray-50">
                  <th className="border border-gray-300 px-4 py-2 text-left">Plan</th>
                  <th className="border border-gray-300 px-4 py-2 text-left">Rate Limit</th>
                  <th className="border border-gray-300 px-4 py-2 text-left">Daily Limit</th>
                  <th className="border border-gray-300 px-4 py-2 text-left">Price</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Free</td>
                  <td className="border border-gray-300 px-4 py-2">10 requests/minute</td>
                  <td className="border border-gray-300 px-4 py-2">100 requests/day</td>
                  <td className="border border-gray-300 px-4 py-2">$0/month</td>
                </tr>
                <tr className="bg-blue-50">
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Basic</td>
                  <td className="border border-gray-300 px-4 py-2">50 requests/minute</td>
                  <td className="border border-gray-300 px-4 py-2">1,000 requests/day</td>
                  <td className="border border-gray-300 px-4 py-2">$29/month</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Professional</td>
                  <td className="border border-gray-300 px-4 py-2">200 requests/minute</td>
                  <td className="border border-gray-300 px-4 py-2">10,000 requests/day</td>
                  <td className="border border-gray-300 px-4 py-2">$99/month</td>
                </tr>
                <tr className="bg-green-50">
                  <td className="border border-gray-300 px-4 py-2 font-semibold">Enterprise</td>
                  <td className="border border-gray-300 px-4 py-2">1,000 requests/minute</td>
                  <td className="border border-gray-300 px-4 py-2">100,000 requests/day</td>
                  <td className="border border-gray-300 px-4 py-2">Custom pricing</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Support */}
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Need Help?</h2>
          <p className="text-gray-600 mb-6">
            Our team is here to help you integrate misinformation detection into your applications.
          </p>
          <div className="space-x-4">
            <a
              href="/contact"
              className="inline-block bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Contact Support
            </a>
            <a
              href="/api-pricing"
              className="inline-block bg-gray-100 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
            >
              View Pricing
            </a>
          </div>
        </div>
      </div>
    </div>
  );
} 