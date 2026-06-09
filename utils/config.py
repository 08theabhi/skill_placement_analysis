import os
from dotenv import load_dotenv
load_dotenv(".env")

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://skilluser:skillpass@localhost:5432/placementai")
    SYNC_DATABASE_URL: str = os.getenv("SYNC_DATABASE_URL", "postgresql://skilluser:skillpass@localhost:5432/placementai")
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./chroma_db")
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "placement_intelligence")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "placement-ai-secret-key-2024")
    MODEL_STORE_PATH: str = os.getenv("MODEL_STORE_PATH", "./ml_models")
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")

settings = Settings()
