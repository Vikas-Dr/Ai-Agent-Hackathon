"""
Central configuration module for ContentPulse.
Loads environment variables and exports constants for the entire system.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from .env (if it exists)
load_dotenv()

# ==================== CONTENT CONSTANTS ====================
TOPICS: list[str] = [
    "AI/ML",
    "DevOps",
    "Cloud",
    "Security",
    "Data Engineering",
    "Frontend",
    "Backend",
    "Mobile",
    "Platform",
    "Leadership",
]

FORMATS: list[str] = [
    "blog",
    "video",
    "infographic",
    "case_study",
    "whitepaper",
    "podcast",
    "newsletter",
]

AUDIENCE_SEGMENTS: list[str] = [
    "developers",
    "managers",
    "executives",
    "general_tech",
]

PERFORMANCE_WEIGHTS: dict[str, float] = {
    "views": 0.4,
    "engagement_rate": 0.3,
    "conversions": 0.2,
    "search_rank": 0.1,
}

# ==================== LLM & ENV SETTINGS ====================
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
MOCK_LLM: bool = os.getenv("MOCK_LLM", "true").lower() in ("true", "1", "yes")

# ==================== DATA & PATHS ====================
PROJECT_ROOT: Path = Path(__file__).parent
DATA_PATH: Path = Path(os.getenv("DATA_PATH", "data/sample_content_data.csv"))
LOGS_DIR: Path = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# ==================== VALIDATION ====================
if not MOCK_LLM and not GOOGLE_API_KEY:
    raise ValueError("MOCK_LLM=false but GOOGLE_API_KEY not set in .env")

__all__ = [
    "TOPICS",
    "FORMATS",
    "AUDIENCE_SEGMENTS",
    "PERFORMANCE_WEIGHTS",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "GOOGLE_API_KEY",
    "MOCK_LLM",
    "PROJECT_ROOT",
    "DATA_PATH",
    "LOGS_DIR",
    "ASSETS_DIR",
]
