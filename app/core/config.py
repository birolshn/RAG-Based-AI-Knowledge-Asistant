import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Proje kök dizini
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Veri dizinleri
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
DB_DIR = DATA_DIR / "db"

# Dizinleri otomatik oluştur
DOCS_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# Model ayarları
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# RAG ayarları
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "3"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "3"))
MEMORY_SIZE = int(os.getenv("MEMORY_SIZE", "5"))

# Desteklenen dosya uzantıları
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".md"}

# Logging
LOG_FILE = BASE_DIR / "rag_log.txt"
