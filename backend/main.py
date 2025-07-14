from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from transformers.pipelines import pipeline
import os
from dotenv import load_dotenv
from fact_check_api import check_claim_with_google
from fever_evidence_corpus import get_fever_corpus
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import time
from collections import defaultdict
import secrets
# from db import AsyncSessionLocal  # Removed for demo mode

# Authentication removed - using simplified demo mode
# Database imports removed for demo mode
# from sqlalchemy.ext.asyncio import AsyncSession
# from models import ApiKey, User, ApiUsage
# from sqlalchemy.future import select
# from sqlalchemy import update
# import smtplib
# from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key Management
API_KEYS = {
    "demo_key": {"tier": "free", "rate_limit": 10, "daily_limit": 100},
    "basic_key": {"tier": "basic", "rate_limit": 50, "daily_limit": 1000},
    "pro_key": {"tier": "pro", "rate_limit": 200, "daily_limit": 10000},
    "enterprise_key": {"tier": "enterprise", "rate_limit": 1000, "daily_limit": 100000},
}

# Rate limiting storage
request_counts = defaultdict(
    lambda: {
        "count": 0,
        "last_reset": time.time(),
        "daily_count": 0,
        "daily_reset": time.time(),
    }
)

# Security
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key and check rate limits - simplified for demo mode."""
    api_key = credentials.credentials

    # For demo mode, accept any key or use demo_key as default
    if api_key not in API_KEYS:
        api_key = "demo_key"  # Default to demo key if invalid

    # Check rate limits
    key_info = API_KEYS[api_key]
    current_time = time.time()

    # Reset counters if needed
    if current_time - request_counts[api_key]["last_reset"] > 60:  # 1 minute window
        request_counts[api_key]["count"] = 0
        request_counts[api_key]["last_reset"] = current_time

    if current_time - request_counts[api_key]["daily_reset"] > 86400:  # 24 hours
        request_counts[api_key]["daily_count"] = 0
        request_counts[api_key]["daily_reset"] = current_time

    # Check rate limits
    if request_counts[api_key]["count"] >= key_info["rate_limit"]:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    if request_counts[api_key]["daily_count"] >= key_info["daily_limit"]:
        raise HTTPException(status_code=429, detail="Daily limit exceeded")

    # Increment counters
    request_counts[api_key]["count"] += 1
    request_counts[api_key]["daily_count"] += 1

    return {"api_key": api_key, "tier": key_info["tier"]}


# --- Load your models and tools ONCE on startup ---
# Option A: Your fine-tuned model (uncomment after training)
model_dir = os.path.abspath("./my_misinformation_model")
claim_classifier = pipeline("text-classification", model=model_dir)

# Option B: An off-the-shelf claim extraction model
claim_extractor = pipeline(
    "question-answering", model="distilbert-base-cased-distilled-squad"
)

# Initialize FEVER evidence corpus
logger.info("Initializing FEVER evidence corpus...")
fever_corpus = get_fever_corpus()
logger.info(f"FEVER corpus stats: {fever_corpus.get_corpus_stats()}")

app = FastAPI(
    title="Misinformation Detector API",
    description="Advanced misinformation detection with multi-source verification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class AnalyzeRequest(BaseModel):
    source_text: str
    source_url: str | None = None


# Authentication models removed - using demo mode


# Database session removed for demo mode
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session


def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        # Try to get the headline
        headline = soup.find("h1")
        if headline:
            headline_text = headline.get_text()
        else:
            headline_text = ""
        # Get all paragraph texts and join them
        paragraphs = soup.find_all("p")
        body_text = " ".join([p.get_text() for p in paragraphs])
        return headline_text + "\n" + body_text
    except Exception as e:
        print(f"Error scraping URL: {e}")
        return None


def analyze_language_patterns(text: str) -> Dict[str, Any]:
    """
    Analyze text for language patterns that might indicate bias or misinformation.
    """
    analysis = {
        "emotional_language": 0,
        "certainty_indicators": 0,
        "urgency_indicators": 0,
        "conspiracy_indicators": 0,
        "red_flags": [],
    }

    text_lower = text.lower()

    # Emotional language patterns
    emotional_words = [
        "shocking",
        "outrageous",
        "terrifying",
        "amazing",
        "incredible",
        "unbelievable",
        "scandalous",
        "corrupt",
        "evil",
        "heroic",
    ]
    analysis["emotional_language"] = sum(
        1 for word in emotional_words if word in text_lower
    )

    # Certainty indicators
    certainty_words = [
        "definitely",
        "absolutely",
        "certainly",
        "without doubt",
        "proven",
        "scientific fact",
        "undeniable",
        "irrefutable",
    ]
    analysis["certainty_indicators"] = sum(
        1 for word in certainty_words if word in text_lower
    )

    # Urgency indicators
    urgency_words = [
        "urgent",
        "breaking",
        "just in",
        "exclusive",
        "you won't believe",
        "act now",
        "limited time",
        "don't miss",
    ]
    analysis["urgency_indicators"] = sum(
        1 for word in urgency_words if word in text_lower
    )

    # Conspiracy indicators
    conspiracy_words = [
        "they don't want you to know",
        "mainstream media",
        "establishment",
        "cover up",
        "hidden truth",
        "secret agenda",
        "elite",
        "deep state",
    ]
    analysis["conspiracy_indicators"] = sum(
        1 for word in conspiracy_words if word in text_lower
    )

    # Red flags
    if analysis["emotional_language"] > 3:
        analysis["red_flags"].append("High emotional language detected")
    if analysis["certainty_indicators"] > 2:
        analysis["red_flags"].append("Excessive certainty claims")
    if analysis["urgency_indicators"] > 2:
        analysis["red_flags"].append("Urgency indicators suggest clickbait")
    if analysis["conspiracy_indicators"] > 1:
        analysis["red_flags"].append("Conspiracy language detected")

    return analysis


def generate_educational_content(
    verdict: str, confidence: float, red_flags: List[str]
) -> Dict[str, Any]:
    """
    Generate educational content based on analysis results.
    """
    educational = {
        "tips": [],
        "why_this_matters": "",
        "how_to_spot_similar": [],
        "related_topics": [],
    }

    if verdict == "REFUTED":
        educational["tips"].extend(
            [
                "Always verify claims with multiple reliable sources",
                "Check if the source has a history of accuracy",
                "Look for primary sources and original research",
                "Be skeptical of claims that seem too good or bad to be true",
            ]
        )
        educational["why_this_matters"] = (
            "False information can spread quickly and influence important decisions. Fact-checking helps protect yourself and others from being misled."
        )

    elif verdict == "SUPPORTED":
        educational["tips"].extend(
            [
                "Even true claims should be verified with multiple sources",
                "Consider the context and timing of the information",
                "Check if the information is current and relevant",
                "Look for expert consensus on the topic",
            ]
        )
        educational["why_this_matters"] = (
            "Accurate information is crucial for making informed decisions. However, even true claims can be presented in misleading ways."
        )

    if red_flags:
        educational["how_to_spot_similar"].extend(
            [
                "Watch for excessive emotional language",
                "Be cautious of claims that seem too certain",
                "Question urgent or exclusive claims",
                "Look for conspiracy language patterns",
            ]
        )

    return educational


def analyze_source_credibility(url: str) -> Dict[str, Any]:
    """
    Analyze the credibility of a source URL.
    """
    credibility = {
        "domain_analysis": {},
        "reputation_score": 50,
        "warning_signs": [],
        "trust_indicators": [],
    }

    if not url:
        return credibility

    try:
        domain = url.split("//")[-1].split("/")[0].lower()

        # Known reliable domains
        reliable_domains = [
            "reuters.com",
            "ap.org",
            "bbc.com",
            "npr.org",
            "pbs.org",
            "factcheck.org",
            "snopes.com",
            "politifact.com",
        ]

        # Known unreliable domains
        unreliable_domains = ["infowars.com", "naturalnews.com", "beforeitsnews.com"]

        if domain in reliable_domains:
            credibility["reputation_score"] = 90
            credibility["trust_indicators"].append(
                "Known reliable fact-checking source"
            )
        elif domain in unreliable_domains:
            credibility["reputation_score"] = 10
            credibility["warning_signs"].append("Known unreliable source")

        # Check for HTTPS
        if url.startswith("https://"):
            credibility["trust_indicators"].append("Secure connection (HTTPS)")
        else:
            credibility["warning_signs"].append("Insecure connection (HTTP)")

        # Check for suspicious domain patterns
        if re.search(r"\d{4,}", domain):
            credibility["warning_signs"].append("Domain contains many numbers")

        credibility["domain_analysis"] = {
            "domain": domain,
            "is_secure": url.startswith("https://"),
            "has_numbers": bool(re.search(r"\d", domain)),
        }

    except Exception as e:
        logger.error(f"Error analyzing source credibility: {e}")

    return credibility


def analyze_claim_with_fever_evidence(claim: str) -> dict:
    """
    Analyze a claim using FEVER evidence corpus.

    Args:
        claim: The claim to analyze

    Returns:
        Dictionary with evidence analysis results
    """
    try:
        # Search for relevant evidence
        evidence_results = fever_corpus.search_evidence(claim, top_k=5)

        if not evidence_results:
            return {
                "evidence_found": False,
                "message": "No relevant evidence found in FEVER corpus",
            }

        # Analyze evidence relevance and consistency
        total_score = sum(result["relevance_score"] for result in evidence_results)
        avg_score = total_score / len(evidence_results)

        # Determine if evidence supports, contradicts, or is neutral to the claim
        supporting_evidence = []
        contradicting_evidence = []
        neutral_evidence = []

        for evidence in evidence_results:
            # Simple keyword-based analysis (can be enhanced with more sophisticated NLP)
            claim_lower = claim.lower()
            evidence_lower = evidence["content"].lower()

            # Check for supporting keywords
            supporting_keywords = [
                "true",
                "correct",
                "accurate",
                "confirmed",
                "verified",
                "fact",
            ]
            contradicting_keywords = [
                "false",
                "incorrect",
                "inaccurate",
                "debunked",
                "misleading",
                "myth",
            ]

            support_count = sum(
                1 for keyword in supporting_keywords if keyword in evidence_lower
            )
            contradict_count = sum(
                1 for keyword in contradicting_keywords if keyword in evidence_lower
            )

            if support_count > contradict_count:
                supporting_evidence.append(evidence)
            elif contradict_count > support_count:
                contradicting_evidence.append(evidence)
            else:
                neutral_evidence.append(evidence)

        # Calculate confidence based on evidence
        confidence = min(avg_score * 100, 95)  # Cap at 95%

        # Determine verdict based on evidence
        if len(supporting_evidence) > len(contradicting_evidence):
            verdict = "SUPPORTED"
            credibility_score = min(70 + confidence, 95)
        elif len(contradicting_evidence) > len(supporting_evidence):
            verdict = "REFUTED"
            credibility_score = max(5, 30 - confidence)
        else:
            verdict = "NEUTRAL"
            credibility_score = 50

        return {
            "evidence_found": True,
            "verdict": verdict,
            "credibility_score": credibility_score,
            "confidence": confidence,
            "total_evidence": len(evidence_results),
            "supporting_evidence": len(supporting_evidence),
            "contradicting_evidence": len(contradicting_evidence),
            "neutral_evidence": len(neutral_evidence),
            "top_evidence": evidence_results[:3],  # Top 3 most relevant pieces
            "analysis_method": "FEVER_evidence_corpus",
        }

    except Exception as e:
        logger.error(f"Error analyzing claim with FEVER evidence: {e}")
        return {
            "evidence_found": False,
            "error": str(e),
            "message": "Error occurred during FEVER evidence analysis",
        }


async def get_api_key_user(request: Request):
    """Get API key user information - simplified for demo mode."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        # For demo mode, use default demo key
        return {
            "user_id": 1,
            "email": "demo@example.com",
            "api_key": "demo_key",
            "tier": "demo",
        }

    api_key = auth.split(" ", 1)[1]

    # For demo mode, accept any key and return demo user
    return {
        "user_id": 1,
        "email": "demo@example.com",
        "api_key": api_key,
        "tier": "demo",
    }


async def check_rate_limit(api_user: dict = Depends(get_api_key_user)):
    """Check rate limits - simplified for demo mode."""
    # For demo mode, use generous limits
    tier_limits = {
        "demo": {"per_minute": 100, "per_day": 10000},
        "free": {"per_minute": 10, "per_day": 100},
        "basic": {"per_minute": 50, "per_day": 1000},
        "pro": {"per_minute": 200, "per_day": 10000},
        "enterprise": {"per_minute": 1000, "per_day": 100000},
    }
    tier = api_user.get("tier", "demo")
    limits = tier_limits.get(tier, tier_limits["demo"])

    # For demo mode, we'll use the existing request_counts system
    api_key = api_user.get("api_key", "demo_key")
    current_time = time.time()

    # Reset counters if needed
    if current_time - request_counts[api_key]["last_reset"] > 60:  # 1 minute window
        request_counts[api_key]["count"] = 0
        request_counts[api_key]["last_reset"] = current_time

    if current_time - request_counts[api_key]["daily_reset"] > 86400:  # 24 hours
        request_counts[api_key]["daily_count"] = 0
        request_counts[api_key]["daily_reset"] = current_time

    # Check rate limits
    if request_counts[api_key]["count"] >= limits["per_minute"]:
        raise HTTPException(status_code=429, detail="Rate limit exceeded (per minute)")

    if request_counts[api_key]["daily_count"] >= limits["per_day"]:
        raise HTTPException(status_code=429, detail="Daily limit exceeded")

    # Increment counters
    request_counts[api_key]["count"] += 1
    request_counts[api_key]["daily_count"] += 1

    return


@app.post("/analyze")
async def analyze_content(
    request: AnalyzeRequest,
    api_user: dict = Depends(get_api_key_user),
    rate_limit=Depends(check_rate_limit),
):
    """
    Analyze content for misinformation with tier-based features.

    Free tier: Basic analysis
    Basic tier: + Language analysis
    Pro tier: + Source credibility + Educational content
    Enterprise tier: + All features + Priority processing
    """
    tier = api_user["tier"]

    text_to_analyze = request.source_text
    source_url = request.source_url

    # Handle if input is a URL
    if text_to_analyze and text_to_analyze.strip().startswith(("http://", "https://")):
        source_url = text_to_analyze.strip()
        text_to_analyze = extract_text_from_url(source_url)
        if not text_to_analyze:
            return {"error": "Could not fetch or parse content from URL."}
    elif source_url and not text_to_analyze:
        text_to_analyze = extract_text_from_url(source_url)
        if not text_to_analyze:
            return {"error": "Could not fetch or parse content from URL."}

    if not text_to_analyze:
        return {"error": "Input text is empty."}

    # 1. Extract potential claims (improved)
    context = text_to_analyze[:4000]  # Limit context size for the model
    try:
        extracted_claim_result = claim_extractor(
            inputs={
                "question": "What is the main claim or headline of this article?",
                "context": context,
            }
        )
        # Handle the result as a dictionary
        if isinstance(extracted_claim_result, dict):
            main_claim = str(extracted_claim_result.get("answer", ""))
        else:
            main_claim = ""
    except Exception as e:
        logger.error(f"Error extracting claim: {e}")
        main_claim = ""

    # Check for short or meaningless claims
    if not main_claim or len(main_claim.strip()) < 10:
        logger.info(
            "Could not extract a meaningful claim, falling back to using initial text."
        )
        # Fallback to using the first part of the text if no specific claim is extracted
        # Try to take the first 3 sentences
        sentences = re.split(r"(?<=[.!?])\s+", text_to_analyze)
        main_claim = " ".join(sentences[:3])

        # If sentences are very short, fall back to character count
        if len(main_claim.strip()) < 20:
            main_claim = text_to_analyze[:500]

        # If the text is fundamentally too short, then we return an error.
        if not main_claim or len(main_claim.strip()) < 10:
            return {
                "error": "The provided text is too short for a meaningful analysis."
            }

    # Initialize response with basic analysis
    response = {
        "analyzed_claim": main_claim,
        "tier": tier,
        "analysis_timestamp": datetime.now().isoformat(),
    }

    # 2. Basic analysis (all tiers)
    fever_analysis = analyze_claim_with_fever_evidence(main_claim)

    if fever_analysis.get("evidence_found", False):
        response.update(
            {
                "credibility_score": fever_analysis["credibility_score"],
                "verdict": fever_analysis["verdict"],
                "confidence": fever_analysis["confidence"],
                "analysis_method": fever_analysis["analysis_method"],
            }
        )
    else:
        # Fallback to Google Fact Check API
        verdict = check_claim_with_google(main_claim)
        if verdict:
            credibility_score = 50  # Neutral
            if "False" in verdict["verdict"] or "Misleading" in verdict["verdict"]:
                credibility_score = 10
            elif "True" in verdict["verdict"] or "Accurate" in verdict["verdict"]:
                credibility_score = 90

            response.update(
                {
                    "credibility_score": credibility_score,
                    "verdict": verdict["verdict"],
                    "confidence": 75,
                    "analysis_method": "Google_Fact_Check_API",
                }
            )
        else:
            # Use fine-tuned model as final fallback
            try:
                model_result = claim_classifier(main_claim)
                if (
                    model_result
                    and isinstance(model_result, list)
                    and len(model_result) > 0
                ):
                    model_verdict = model_result[0]
                    label_map = {0: "False", 1: "Half-True", 2: "True"}
                    label = int(str(model_verdict.get("label", "0")).split("_")[-1])
                    verdict_text = label_map.get(label, "Unknown")
                    score = float(model_verdict.get("score", 0.5))

                    response.update(
                        {
                            "credibility_score": int(score * 100),
                            "verdict": verdict_text,
                            "confidence": int(score * 100),
                            "analysis_method": "Fine_tuned_model",
                        }
                    )
            except Exception as e:
                logger.error(f"Error in model analysis: {e}")
                response["error"] = f"Model analysis error: {str(e)}"

    # 3. Language analysis (Basic tier and above)
    if tier in ["basic", "pro", "enterprise"]:
        language_analysis = analyze_language_patterns(text_to_analyze)
        response["language_analysis"] = language_analysis

    # 4. Source credibility analysis (Pro tier and above)
    if tier in ["pro", "enterprise"]:
        source_analysis = analyze_source_credibility(source_url or "")
        response["source_analysis"] = source_analysis

    # 5. Educational content (Pro tier and above)
    if tier in ["pro", "enterprise"]:
        red_flags = response.get("language_analysis", {}).get("red_flags", [])
        educational_content = generate_educational_content(
            response.get("verdict", "NEUTRAL"),
            response.get("confidence", 50),
            red_flags,
        )
        response["educational_content"] = educational_content

    # 6. Enhanced evidence (Enterprise tier only)
    if tier == "enterprise" and fever_analysis.get("evidence_found", False):
        response["evidence_summary"] = {
            "total_evidence": fever_analysis["total_evidence"],
            "supporting": fever_analysis["supporting_evidence"],
            "contradicting": fever_analysis["contradicting_evidence"],
            "neutral": fever_analysis["neutral_evidence"],
        }
        response["top_evidence"] = fever_analysis["top_evidence"]

    return response


@app.get("/corpus/stats")
async def get_corpus_stats():
    """Get statistics about the FEVER evidence corpus."""
    return fever_corpus.get_corpus_stats()


@app.get("/corpus/search")
async def search_corpus(query: str, top_k: int = 5):
    """Search the FEVER evidence corpus for a query."""
    results = fever_corpus.search_evidence(query, top_k=top_k)
    return {"query": query, "results": results, "total_results": len(results)}


@app.get("/educational/tips")
async def get_fact_checking_tips():
    """Get general fact-checking tips and educational content."""
    return {
        "tips": [
            "Check multiple sources before believing a claim",
            "Look for primary sources and original research",
            "Be skeptical of claims that seem too good or bad to be true",
            "Check the date of the information - old news can be misleading",
            "Look for expert consensus on scientific topics",
            "Be aware of your own biases and confirmation bias",
            "Check if the source has a history of accuracy",
            "Look for fact-checking organizations' verdicts",
            "Be cautious of emotional language and urgency",
            "Question claims that contradict established facts",
        ],
        "red_flags": [
            "Excessive emotional language",
            "Claims that seem too certain",
            "Urgency or exclusivity claims",
            "Conspiracy language patterns",
            "Lack of specific details or sources",
            "Claims that appeal to authority without evidence",
            "Information that confirms your existing beliefs too perfectly",
        ],
        "reliable_sources": [
            "Reuters",
            "Associated Press",
            "BBC",
            "NPR",
            "PBS",
            "FactCheck.org",
            "Snopes",
            "PolitiFact",
            "AP Fact Check",
        ],
    }


@app.get("/api/keys")
async def get_api_keys():
    """Get available API key tiers and their features."""
    return {
        "tiers": {
            "free": {
                "name": "Free",
                "price": "$0/month",
                "rate_limit": "10 requests/minute",
                "daily_limit": "100 requests/day",
                "features": [
                    "Basic misinformation analysis",
                    "Credibility scoring",
                    "Verdict classification",
                ],
            },
            "basic": {
                "name": "Basic",
                "price": "$29/month",
                "rate_limit": "50 requests/minute",
                "daily_limit": "1,000 requests/day",
                "features": [
                    "All Free features",
                    "Language pattern analysis",
                    "Red flag detection",
                ],
            },
            "pro": {
                "name": "Professional",
                "price": "$99/month",
                "rate_limit": "200 requests/minute",
                "daily_limit": "10,000 requests/day",
                "features": [
                    "All Basic features",
                    "Source credibility analysis",
                    "Educational content",
                    "Priority support",
                ],
            },
            "enterprise": {
                "name": "Enterprise",
                "price": "Custom pricing",
                "rate_limit": "1,000 requests/minute",
                "daily_limit": "100,000 requests/day",
                "features": [
                    "All Pro features",
                    "Enhanced evidence analysis",
                    "Custom integrations",
                    "Dedicated support",
                ],
            },
        }
    }


@app.get("/api/usage")
async def get_usage_stats(auth: dict = Depends(verify_api_key)):
    """Get current API usage statistics."""
    api_key = auth["api_key"]
    key_info = API_KEYS[api_key]
    current_usage = request_counts[api_key]

    return {
        "tier": key_info["tier"],
        "rate_limit": key_info["rate_limit"],
        "daily_limit": key_info["daily_limit"],
        "current_usage": {
            "requests_this_minute": current_usage["count"],
            "requests_today": current_usage["daily_count"],
            "remaining_today": max(
                0, key_info["daily_limit"] - current_usage["daily_count"]
            ),
        },
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "fever_corpus": "operational",
            "claim_classifier": "operational",
            "claim_extractor": "operational",
        },
    }


# Authentication endpoints removed - using demo mode with simplified API key system
