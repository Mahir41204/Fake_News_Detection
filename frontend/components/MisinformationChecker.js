"use client";
import { useState, useEffect } from 'react';

export default function MisinformationChecker() {
    const [input, setInput] = useState('');
    const [result, setResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('analysis');
    const [educationalTips, setEducationalTips] = useState(null);
    const apiKey = 'demo_key'; // Demo mode - always use demo key

    useEffect(() => {
        // Load educational tips on component mount
        fetch('/api/educational/tips')
            .then(res => res.json())
            .then(data => setEducationalTips(data))
            .catch(err => console.error('Failed to load tips:', err));
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setResult(null);
        setError('');
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify({ source_text: input }),
            });
            
            if (response.status === 401) {
                throw new Error('Demo mode error. Please try again.');
            } else if (response.status === 429) {
                throw new Error('Rate limit exceeded. Please try again later.');
            } else if (!response.ok) {
                throw new Error('Failed to get a response from the server.');
            }
            
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            setResult(data);
            setActiveTab('analysis');
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const getCredibilityColor = (score) => {
        if (score >= 70) return 'text-green-600';
        if (score >= 40) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getCredibilityBgColor = (score) => {
        if (score >= 70) return 'bg-green-100 border-green-300';
        if (score >= 40) return 'bg-yellow-100 border-yellow-300';
        return 'bg-red-100 border-red-300';
    };

    const getVerdictColor = (verdict) => {
        if (verdict === 'SUPPORTED' || verdict === 'True') return 'text-green-700 bg-green-100';
        if (verdict === 'REFUTED' || verdict === 'False') return 'text-red-700 bg-red-100';
        return 'text-yellow-700 bg-yellow-100';
    };

    const getTierBadgeColor = (tier) => {
        switch (tier) {
            case 'free': return 'bg-gray-100 text-gray-700';
            case 'basic': return 'bg-blue-100 text-blue-700';
            case 'pro': return 'bg-purple-100 text-purple-700';
            case 'enterprise': return 'bg-green-100 text-green-700';
            default: return 'bg-gray-100 text-gray-700';
        }
    };

    const ConfidenceMeter = ({ score, confidence }) => (
        <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Credibility Score</span>
                <span className={`text-lg font-bold ${getCredibilityColor(score)}`}>
                    {score}/100
                </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                    className={`h-3 rounded-full transition-all duration-500 ${
                        score >= 70 ? 'bg-green-500' : score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${score}%` }}
                ></div>
            </div>
            {confidence && (
                <div className="mt-2 text-sm text-gray-600">
                    Confidence: {confidence}%
                </div>
            )}
        </div>
    );

    const LanguageAnalysis = ({ analysis }) => (
        <div className="bg-white rounded-lg p-4 border border-gray-200 mb-4">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">Language Analysis</h3>
            <div className="space-y-2">
                <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
                    <span className="font-medium text-gray-700">Emotional Words: </span>
                    <span className="font-bold text-lg text-blue-600">{analysis.emotional_language}</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
                    <span className="font-medium text-gray-700">Certainty Claims: </span>
                    <span className="font-bold text-lg text-purple-600">{analysis.certainty_indicators}</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
                    <span className="font-medium text-gray-700">Urgency Signs: </span>
                    <span className="font-bold text-lg text-orange-600">{analysis.urgency_indicators}</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50">
                    <span className="font-medium text-gray-700">Conspiracy Terms: </span>
                    <span className="font-bold text-lg text-red-600">{analysis.conspiracy_indicators}</span>
                </div>
            </div>
            {analysis.red_flags.length > 0 && (
                <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
                    <h4 className="font-semibold text-red-800 mb-2">⚠️ Red Flags Detected:</h4>
                    <ul className="text-sm text-red-700 space-y-1">
                        {analysis.red_flags.map((flag, index) => (
                            <li key={index} className="flex items-center">
                                <span className="mr-2">•</span>
                                {flag}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );

    const SourceAnalysis = ({ analysis }) => (
        <div className="bg-white rounded-lg p-4 border border-gray-200 mb-4">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">Source Analysis</h3>
            <div className="flex items-center mb-3">
                <span className="text-sm font-medium text-gray-700 mr-2">Reputation Score:</span>
                <span className={`font-bold ${getCredibilityColor(analysis.reputation_score)}`}>
                    {analysis.reputation_score}/100
                </span>
            </div>
            {analysis.trust_indicators.length > 0 && (
                <div className="mb-3">
                    <h4 className="font-semibold text-green-800 mb-2">✅ Trust Indicators:</h4>
                    <ul className="text-sm text-green-700">
                        {analysis.trust_indicators.map((indicator, index) => (
                            <li key={index} className="flex items-center mb-1">
                                <span className="mr-2">✓</span>
                                {indicator}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            {analysis.warning_signs.length > 0 && (
                <div className="mb-3">
                    <h4 className="font-semibold text-red-800 mb-2">⚠️ Warning Signs:</h4>
                    <ul className="text-sm text-red-700">
                        {analysis.warning_signs.map((warning, index) => (
                            <li key={index} className="flex items-center mb-1">
                                <span className="mr-2">•</span>
                                {warning}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );

    const EducationalContent = ({ content }) => (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <h3 className="text-lg font-semibold mb-3 text-blue-800">💡 Why This Matters</h3>
            <p className="text-blue-700 mb-4">{content.why_this_matters}</p>
            
            <h4 className="font-semibold text-blue-800 mb-2">📚 Fact-Checking Tips:</h4>
            <ul className="text-sm text-blue-700 mb-4">
                {content.tips.map((tip, index) => (
                    <li key={index} className="flex items-start mb-2">
                        <span className="mr-2 mt-1">•</span>
                        {tip}
                    </li>
                ))}
            </ul>
            
            {content.how_to_spot_similar.length > 0 && (
                <>
                    <h4 className="font-semibold text-blue-800 mb-2">🔍 How to Spot Similar Claims:</h4>
                    <ul className="text-sm text-blue-700">
                        {content.how_to_spot_similar.map((tip, index) => (
                            <li key={index} className="flex items-start mb-2">
                                <span className="mr-2 mt-1">•</span>
                                {tip}
                            </li>
                        ))}
                    </ul>
                </>
            )}
        </div>
    );

    const EvidenceDisplay = ({ evidence }) => (
        <div className="bg-white rounded-lg p-4 border border-gray-200 mb-4">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">📊 Evidence Summary</h3>
            <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{evidence.supporting}</div>
                    <div className="text-sm text-gray-600">Supporting</div>
                </div>
                <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{evidence.contradicting}</div>
                    <div className="text-sm text-gray-600">Contradicting</div>
                </div>
                <div className="text-center">
                    <div className="text-2xl font-bold text-gray-600">{evidence.neutral}</div>
                    <div className="text-sm text-gray-600">Neutral</div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
            <div className="max-w-6xl mx-auto px-4">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-800 mb-2">
                        🔍 Misinformation Detector
                    </h1>
                    <p className="text-gray-600">
                        Analyze articles, claims, and content for accuracy and credibility
                    </p>
                </div>

                {/* Input Form */}
                <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Enter article text or URL
                            </label>
                <textarea
                                className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                rows="8"
                                placeholder="Paste article text here, or enter a URL to analyze..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                        </div>
                <button
                    type="submit"
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    disabled={isLoading}
                >
                            {isLoading ? (
                                <>
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                    Analyzing...
                                </>
                            ) : (
                                '🔍 Analyze Content'
                            )}
                </button>
            </form>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
                        <div className="flex items-center">
                            <span className="text-red-600 mr-2">⚠️</span>
                            <span className="text-red-800">{error}</span>
                        </div>
                    </div>
                )}

            {result && (
                    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                        {/* Tab Navigation */}
                        <div className="border-b border-gray-200">
                            <nav className="flex">
                                <button
                                    onClick={() => setActiveTab('analysis')}
                                    className={`px-6 py-3 font-medium text-sm ${
                                        activeTab === 'analysis'
                                            ? 'border-b-2 border-blue-500 text-blue-600'
                                            : 'text-gray-500 hover:text-gray-700'
                                    }`}
                                >
                                    📊 Analysis Results
                                </button>
                                <button
                                    onClick={() => setActiveTab('evidence')}
                                    className={`px-6 py-3 font-medium text-sm ${
                                        activeTab === 'evidence'
                                            ? 'border-b-2 border-blue-500 text-blue-600'
                                            : 'text-gray-500 hover:text-gray-700'
                                    }`}
                                >
                                    📚 Evidence & Sources
                                </button>
                                <button
                                    onClick={() => setActiveTab('education')}
                                    className={`px-6 py-3 font-medium text-sm ${
                                        activeTab === 'education'
                                            ? 'border-b-2 border-blue-500 text-blue-600'
                                            : 'text-gray-500 hover:text-gray-700'
                                    }`}
                                >
                                    🎓 Learn More
                                </button>
                            </nav>
                        </div>

                        {/* Tab Content */}
                        <div className="p-6">
                            {activeTab === 'analysis' && (
                                <div>
                                    {/* Main Results */}
                                    <div className={`rounded-lg p-6 mb-6 ${getCredibilityBgColor(result.credibility_score)}`}>
                                        <div className="flex items-center justify-between mb-4">
                                            <h2 className="text-2xl font-bold text-gray-800">Analysis Results</h2>
                                            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getVerdictColor(result.verdict || result.model_verdict)}`}>
                                                {result.verdict || result.model_verdict || 'Unknown'}
                                            </span>
                                        </div>
                                        
                                        <div className="mb-4">
                                            <h3 className="font-semibold text-gray-700 mb-2">Analyzed Claim:</h3>
                                            <p className="text-gray-800 italic">"{result.analyzed_claim}"</p>
                                        </div>

                                        <ConfidenceMeter score={result.credibility_score} confidence={result.confidence} />
                                    </div>

                                    {/* Language Analysis */}
                                    {result.language_analysis && (
                                        <LanguageAnalysis analysis={result.language_analysis} />
                                    )}

                                    {/* Source Analysis */}
                                    {result.source_analysis && (
                                        <SourceAnalysis analysis={result.source_analysis} />
                                    )}

                                    {/* Educational Content */}
                                    {result.educational_content && (
                                        <EducationalContent content={result.educational_content} />
                                    )}
                                </div>
                            )}

                            {activeTab === 'evidence' && (
                                <div>
                                    {result.evidence_summary && (
                                        <EvidenceDisplay evidence={result.evidence_summary} />
                                    )}
                                    
                                    {result.top_evidence && result.top_evidence.length > 0 && (
                                        <div className="bg-white rounded-lg p-4 border border-gray-200">
                                            <h3 className="text-lg font-semibold mb-3 text-gray-800">Top Evidence</h3>
                                            {result.top_evidence.map((evidence, index) => (
                                                <div key={index} className="mb-4 p-3 bg-gray-50 rounded-lg">
                                                    <div className="flex justify-between items-start mb-2">
                                                        <span className="text-sm font-medium text-gray-600">
                                                            Evidence #{index + 1}
                                                        </span>
                                                        <span className="text-sm text-blue-600">
                                                            Score: {(evidence.relevance_score * 100).toFixed(1)}%
                                                        </span>
                                                    </div>
                                                    <p className="text-gray-800 text-sm">{evidence.content}</p>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {result.results && result.results.length > 0 && (
                                        <div className="bg-white rounded-lg p-4 border border-gray-200 mt-4">
                                            <h3 className="text-lg font-semibold mb-3 text-gray-800">External Fact-Checking Results</h3>
                                            {result.results.map((item, index) => (
                                                <div key={index} className="mb-4 p-3 border-l-4 border-blue-500 bg-blue-50 rounded-r-lg">
                                                    <p className="font-medium text-gray-800 mb-1">{item.claim}</p>
                                                    <p className="text-sm text-gray-600 mb-2">
                                                        <span className="font-medium">Verdict:</span> {item.verdict}
                                                    </p>
                                                    {item.source && (
                                                        <a 
                                                            href={item.source} 
                                                            target="_blank" 
                                                            rel="noopener noreferrer" 
                                                            className="text-blue-600 hover:text-blue-800 text-sm underline"
                                                        >
                                                            View Source →
                                                        </a>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {activeTab === 'education' && (
                                <div>
                                    {educationalTips && (
                                        <div className="space-y-6">
                                            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                                                <h3 className="text-lg font-semibold mb-3 text-green-800">✅ Fact-Checking Tips</h3>
                                                <ul className="text-sm text-green-700 space-y-2">
                                                    {educationalTips.tips.map((tip, index) => (
                                                        <li key={index} className="flex items-start">
                                                            <span className="mr-2 mt-1">•</span>
                                                            {tip}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>

                                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                                <h3 className="text-lg font-semibold mb-3 text-red-800">⚠️ Red Flags to Watch For</h3>
                                                <ul className="text-sm text-red-700 space-y-2">
                                                    {educationalTips.red_flags.map((flag, index) => (
                                                        <li key={index} className="flex items-start">
                                                            <span className="mr-2 mt-1">•</span>
                                                            {flag}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>

                                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                                <h3 className="text-lg font-semibold mb-3 text-blue-800">📰 Reliable Sources</h3>
                                                <div className="text-sm text-blue-700">
                                                    <p className="mb-2">Trusted fact-checking organizations:</p>
                                                    <div className="grid grid-cols-2 gap-2">
                                                        {educationalTips.reliable_sources.map((source, index) => (
                                                            <span key={index} className="bg-white px-2 py-1 rounded text-xs">
                                                                {source}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}