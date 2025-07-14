#!/usr/bin/env python3
"""
Test script to demonstrate FEVER evidence corpus functionality.
"""

import requests
import json
import time

def test_fever_corpus():
    """Test the FEVER evidence corpus functionality."""
    
    # Base URL for the FastAPI server
    base_url = "http://localhost:8000"
    
    print("Testing FEVER Evidence Corpus Integration")
    print("=" * 50)
    
    # Test 1: Get corpus statistics
    print("\n1. Getting corpus statistics...")
    try:
        response = requests.get(f"{base_url}/corpus/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Corpus stats: {stats}")
        else:
            print(f"✗ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting stats: {e}")
    
    # Test 2: Search corpus
    print("\n2. Testing corpus search...")
    test_queries = [
        "climate change",
        "vaccines",
        "election fraud",
        "COVID-19"
    ]
    
    for query in test_queries:
        try:
            response = requests.get(f"{base_url}/corpus/search", params={"query": query, "top_k": 3})
            if response.status_code == 200:
                results = response.json()
                print(f"✓ Search for '{query}': {results['total_results']} results")
                if results['results']:
                    top_result = results['results'][0]
                    print(f"  Top result: {top_result['title']} (score: {top_result['relevance_score']:.3f})")
            else:
                print(f"✗ Failed to search for '{query}': {response.status_code}")
        except Exception as e:
            print(f"✗ Error searching for '{query}': {e}")
    
    # Test 3: Analyze content with FEVER evidence
    print("\n3. Testing content analysis with FEVER evidence...")
    
    test_claims = [
        {
            "source_text": "Climate change is a hoax created by scientists to get funding.",
            "description": "Climate change denial claim"
        },
        {
            "source_text": "Vaccines cause autism in children.",
            "description": "Anti-vaccine claim"
        },
        {
            "source_text": "The Earth is flat and NASA is hiding the truth.",
            "description": "Flat Earth conspiracy"
        }
    ]
    
    for i, test_case in enumerate(test_claims, 1):
        print(f"\n   Test {i}: {test_case['description']}")
        try:
            response = requests.post(
                f"{base_url}/analyze",
                json={"source_text": test_case['source_text']}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Analysis completed")
                print(f"  Claim: {result.get('analyzed_claim', 'N/A')}")
                print(f"  Verdict: {result.get('verdict', 'N/A')}")
                print(f"  Credibility Score: {result.get('credibility_score', 'N/A')}")
                print(f"  Method: {result.get('analysis_method', 'N/A')}")
                
                if 'evidence_summary' in result:
                    evidence = result['evidence_summary']
                    print(f"  Evidence: {evidence['supporting']} supporting, {evidence['contradicting']} contradicting")
            else:
                print(f"  ✗ Analysis failed: {response.status_code}")
                print(f"  Response: {response.text}")
                
        except Exception as e:
            print(f"  ✗ Error in analysis: {e}")
    
    print("\n" + "=" * 50)
    print("FEVER Evidence Corpus Test Completed!")

if __name__ == "__main__":
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("You can start it with: uvicorn main:app --reload")
    print()
    
    input("Press Enter to start testing...")
    test_fever_corpus() 