import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
INDEX_DIR = DATA_DIR / "indices"
SAMPLES_DIR = BASE_DIR / "samples"
STATIC_DIR = BASE_DIR / "static"

for directory in (UPLOAD_DIR, INDEX_DIR, SAMPLES_DIR, STATIC_DIR):
    directory.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    app_name: str = "AI Project Intelligence & Risk Advisor"
    version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")

    # Storage paths
    upload_dir: Path = UPLOAD_DIR
    index_dir: Path = INDEX_DIR
    samples_dir: Path = SAMPLES_DIR
    static_dir: Path = STATIC_DIR

    # RAG Settings
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "80"))
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    top_k_retrieval: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))

    # LLM Settings
    default_llm_provider: str = os.getenv("LLM_PROVIDER", "auto")  # 'gemini', 'openai', 'local'
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))


settings = Settings()
