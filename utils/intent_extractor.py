"""
Developer Intent Extractor for DevPulse.
Classifies developer content by search/reading intent from titles and abstracts.
"""

import re
from typing import Optional


INTENT_PATTERNS = {
    "How-To": {
        "keywords": ["how to", "how-to", "guide to", "tutorial", "getting started", "step by step", "walkthrough"],
        "pattern": r"how\s+to|step-by-step|getting\s+started|tutorial|guide|walkthrough",
        "confidence_boost": 0.8
    },
    "Troubleshooting": {
        "keywords": ["fix", "solve", "debug", "error", "issue", "problem", "troubleshoot", "error handling"],
        "pattern": r"fix|solve|debug|error|issue|problem|troubleshoot|error\s+handling",
        "confidence_boost": 0.75
    },
    "Reference": {
        "keywords": ["documentation", "reference", "api docs", "reference guide", "specification", "spec"],
        "pattern": r"documentation|reference|api\s+docs|reference\s+guide|specification",
        "confidence_boost": 0.7
    },
    "Case Study": {
        "keywords": ["case study", "lessons learned", "real world", "production", "deployed"],
        "pattern": r"case\s+study|lessons\s+learned|real\s+world|production|deployed",
        "confidence_boost": 0.75
    },
    "Announcement": {
        "keywords": ["released", "announcing", "introducing", "launch", "new", "beta"],
        "pattern": r"released|announcing|introducing|launch|new\s+feature|beta",
        "confidence_boost": 0.7
    }
}


def extract_developer_intent(title: str, abstract: Optional[str] = None) -> dict:
    """
    Extract and classify developer content intent from title and abstract.
    
    Args:
        title: Article/content title
        abstract: Optional content summary/abstract
    
    Returns:
        Dict with intent_type, confidence, keywords, and reasoning
    """
    if not title:
        return {
            "intent_type": "Unknown",
            "confidence": 0.0,
            "keywords": [],
            "reasoning": "Empty title"
        }
    
    full_text = (title + " " + (abstract or "")).lower()
    intent_scores = {}
    
    for intent_type, intent_config in INTENT_PATTERNS.items():
        score = 0.0
        matched_keywords = []
        
        # Check keywords
        for kw in intent_config["keywords"]:
            if kw in full_text:
                matched_keywords.append(kw)
                score += 0.1
        
        # Check regex pattern
        if re.search(intent_config["pattern"], full_text):
            score += intent_config["confidence_boost"]
        
        if score > 0:
            intent_scores[intent_type] = {
                "score": min(score, 1.0),
                "keywords": matched_keywords
            }
    
    if not intent_scores:
        return {
            "intent_type": "General",
            "confidence": 0.3,
            "keywords": [],
            "reasoning": "No specific intent patterns matched"
        }
    
    # Get highest scoring intent
    best_intent = max(intent_scores.items(), key=lambda x: x[1]["score"])
    intent_type = best_intent[0]
    confidence = best_intent[1]["score"]
    keywords = best_intent[1]["keywords"]
    
    return {
        "intent_type": intent_type,
        "confidence": round(confidence, 2),
        "keywords": list(set(keywords)),  # Unique keywords
        "reasoning": f"Matched {intent_type.lower()} patterns in title and content"
    }


def batch_extract_intents(titles: list[str]) -> list[dict]:
    """Extract intent for multiple titles in batch."""
    return [extract_developer_intent(title) for title in titles]


def intent_distribution(intent_results: list[dict]) -> dict:
    """Calculate distribution of intents across multiple results."""
    distribution = {}
    for result in intent_results:
        intent = result["intent_type"]
        distribution[intent] = distribution.get(intent, 0) + 1
    
    return {
        "distribution": distribution,
        "dominant_intent": max(distribution.items(), key=lambda x: x[1])[0] if distribution else None,
        "total_analyzed": len(intent_results)
    }
