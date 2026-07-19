"""
Central configuration module for DevPulse (ContentPulse for DevRel).
"""
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# ==================== DEVREL CONTENT CONSTANTS ====================
TOPICS: list[str] = [
    "API Design",
    "Authentication",
    "Cloud Infrastructure",
    "Database & Data",
    "DevOps & CI/CD",
    "Frontend Frameworks",
    "Mobile Development",
    "Python & Data Science",
    "Web Security",
    "Serverless & Edge",
]

FORMATS: list[str] = [
    "technical_blog",
    "tutorial",
    "code_example",
    "documentation",
    "case_study",
    "webinar",
    "sample_project",
]

AUDIENCE_SEGMENTS: list[str] = [
    "frontend",
    "backend",
    "devops",
    "architects",
]

PERFORMANCE_WEIGHTS: dict[str, float] = {
    "views": 0.30,
    "engagement_rate": 0.25,
    "conversions": 0.25,
    "search_rank": 0.10,
    "github_stars_growth": 0.10,
}

# ==================== LLM & ENV SETTINGS ====================
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
HF_TOKEN: str = os.getenv("HF_TOKEN", "")
MOCK_LLM: bool = os.getenv("MOCK_LLM", "true").lower() in ("true", "1", "yes")

# ==================== DATA & PATHS ====================
PROJECT_ROOT: Path = Path(__file__).parent
DATA_PATH: Path = Path(os.getenv("DATA_PATH", "data/sample_content_data.csv"))
LOGS_DIR: Path = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# ==================== DEVREL TRENDING TOPICS ====================
TRENDING_DEVREL_TOPICS: list[str] = [
    "AI Agents & MCP",
    "WebAssembly",
    "Platform Engineering",
    "Developer Experience (DX)",
    "Edge Functions",
    "Rust for Systems",
]

# ==================== VALIDATION ====================
if not MOCK_LLM and LLM_PROVIDER == "gemini" and not GOOGLE_API_KEY:
    raise ValueError("MOCK_LLM=false with gemini provider but GOOGLE_API_KEY not set")
if not MOCK_LLM and LLM_PROVIDER == "huggingface" and not HF_TOKEN:
    raise ValueError("MOCK_LLM=false with huggingface provider but HF_TOKEN not set")

__all__ = [
    "TOPICS", "FORMATS", "AUDIENCE_SEGMENTS", "PERFORMANCE_WEIGHTS",
    "LLM_PROVIDER", "LLM_MODEL", "GOOGLE_API_KEY", "HF_TOKEN", "MOCK_LLM",
    "PROJECT_ROOT", "DATA_PATH", "LOGS_DIR", "ASSETS_DIR", "TRENDING_DEVREL_TOPICS",
]
