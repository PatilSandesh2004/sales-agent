"""Easy & Beginner-Friendly Configuration File."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file (check backend/ or root)
load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_EXCEL_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "sales.db"

# LLM Settings (Optional)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

