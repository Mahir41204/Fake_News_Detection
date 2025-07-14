import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("GOOGLE_API_KEY")
API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


def check_claim_with_google(claim_text):
    params = {"query": claim_text, "key": API_KEY}
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if "claims" in data and len(data["claims"]) > 0:
            review = data["claims"][0]["claimReview"][0]
            return {
                "verdict": review.get("textualRating", "No rating found"),
                "original_claim": data["claims"][0].get("text", "N/A"),
                "source_url": review.get("url", "N/A"),
            }
    return None
