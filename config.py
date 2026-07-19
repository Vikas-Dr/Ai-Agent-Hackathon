"""Central configuration for DevPulse."""
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

TOPICS: list[str] = [
    "API Design", "Authentication", "Cloud Infrastructure", "Database & Data",
    "DevOps & CI/CD", "Frontend Frameworks", "Mobile Development",
    "Python & Data Science", "Web Security", "Serverless & Edge",
]

FORMATS: list[str] = [
    "technical_blog", "tutorial", "code_example", "documentation",
    "case_study", "webinar", "sample_project",
]

AUDIENCE_SEGMENTS: list[str] = ["frontend", "backend", "devops", "architects"]

PERFORMANCE_WEIGHTS: dict[str, float] = {
    "views": 0.30, "engagement_rate": 0.25, "conversions": 0.25,
    "search_rank": 0.10, "github_stars_growth": 0.10,
}

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
HF_TOKEN: str = os.getenv("HF_TOKEN", "")
MOCK_LLM: bool = os.getenv("MOCK_LLM", "true").lower() in ("true", "1", "yes")

PROJECT_ROOT: Path = Path(__file__).parent
DATA_PATH: Path = Path(os.getenv("DATA_PATH", "data/sample_content_data.csv"))
LOGS_DIR: Path = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

TRENDING_DEVREL_TOPICS: list[str] = [
    "AI Agents & MCP", "WebAssembly", "Platform Engineering",
    "Developer Experience (DX)", "Edge Functions", "Rust for Systems",
]
