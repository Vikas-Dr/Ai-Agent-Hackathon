"""
SDK Version Drift Detector for DevPulse.
Flags articles with deprecated SDK references for DevRel teams.
"""

import re
from typing import Optional


DEPRECATED_SDKS = {
    "google.generativeai": {
        "name": "Google Generative AI SDK",
        "deprecated_version": "< 0.3.0",
        "replacement": "google.antigravity (new) or google-generativeai >= 0.4.0",
        "severity": "high",
        "pattern": r"import\s+google\.generativeai|from\s+google\s+import\s+generativeai"
    },
    "pydantic_v1": {
        "name": "Pydantic v1",
        "deprecated_version": "v1.x",
        "replacement": "pydantic >= 2.0",
        "severity": "high",
        "pattern": r"from\s+pydantic\s+import|import\s+pydantic\b"
    },
    "requests_old": {
        "name": "Requests (old session handling)",
        "deprecated_version": "< 2.25.0",
        "replacement": "requests >= 2.28.0 or httpx",
        "severity": "medium",
        "pattern": r"requests\.Session\(\)|import\s+requests"
    },
    "fastapi_old": {
        "name": "FastAPI (deprecated patterns)",
        "deprecated_version": "< 0.95.0",
        "replacement": "fastapi >= 0.100.0",
        "severity": "medium",
        "pattern": r"from\s+fastapi\s+import\s+.*deprecated|async\s+def\s+.*deprecated"
    },
    "sqlalchemy_1": {
        "name": "SQLAlchemy 1.x",
        "deprecated_version": "1.x",
        "replacement": "sqlalchemy >= 2.0",
        "severity": "medium",
        "pattern": r"from\s+sqlalchemy\s+import|sqlalchemy\.Column|declarative_base"
    },
    "django_old": {
        "name": "Django (old ORM patterns)",
        "deprecated_version": "< 4.0",
        "replacement": "django >= 4.2",
        "severity": "low",
        "pattern": r"django\.db\.models|from\s+django\s+import\s+models"
    }
}


def detect_deprecated_sdks(content: str, code_blocks: Optional[list[str]] = None) -> dict:
    """
    Scan content and code blocks for deprecated SDK references.
    
    Args:
        content: Article/documentation text
        code_blocks: Optional list of extracted code snippets
    
    Returns:
        Dict with detected deprecated SDKs and severity levels
    """
    if not content:
        return {"deprecated_sdks": [], "has_issues": False}
    
    scan_text = content.lower()
    if code_blocks:
        scan_text += "\n" + "\n".join(code_blocks)
    
    detected = []
    
    for sdk_key, sdk_info in DEPRECATED_SDKS.items():
        # Pattern matching
        matches = re.findall(sdk_info["pattern"], scan_text, re.IGNORECASE)
        
        # Title keyword matching (fallback)
        title_keywords = {
            "google.generativeai": ["google generativeai", "generativeai sdk"],
            "pydantic_v1": ["pydantic v1", "pydantic 1."],
            "requests_old": ["requests session", "requests library"],
            "fastapi_old": ["fastapi deprecated", "fastapi legacy"],
            "sqlalchemy_1": ["sqlalchemy 1", "sqlalchemy v1"],
            "django_old": ["django old", "django legacy"]
        }
        
        if matches or any(kw in scan_text for kw in title_keywords.get(sdk_key, [])):
            detected.append({
                "sdk": sdk_info["name"],
                "key": sdk_key,
                "deprecated_version": sdk_info["deprecated_version"],
                "replacement": sdk_info["replacement"],
                "severity": sdk_info["severity"],
                "match_count": len(matches) if matches else 1
            })
    
    return {
        "deprecated_sdks": sorted(detected, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]]),
        "has_issues": len(detected) > 0,
        "high_severity_count": sum(1 for d in detected if d["severity"] == "high"),
        "medium_severity_count": sum(1 for d in detected if d["severity"] == "medium")
    }


def format_deprecation_warning(sdk_results: dict) -> str:
    """Format deprecation results as markdown warning block."""
    if not sdk_results["has_issues"]:
        return ""
    
    warning = "⚠️ **SDK Deprecation Alerts:**\n\n"
    for sdk in sdk_results["deprecated_sdks"]:
        severity_icon = "🔴" if sdk["severity"] == "high" else "🟡" if sdk["severity"] == "medium" else "🟢"
        warning += f"{severity_icon} **{sdk['sdk']}** ({sdk['severity']})\n"
        warning += f"   - Deprecated: {sdk['deprecated_version']}\n"
        warning += f"   - Upgrade to: {sdk['replacement']}\n\n"
    
    return warning
