import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))
    # Uses faq_replica.json — structured format with intent + questions array + answer
    FAQ_PATH = os.getenv(
        "FAQ_PATH",
        os.path.join(os.path.dirname(__file__), "..", "faq_replica.json")
    )
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    # Combined score threshold (TF-IDF 70% + keyword overlap 30%)
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.17))
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", 500))
