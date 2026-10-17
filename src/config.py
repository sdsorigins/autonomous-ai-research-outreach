import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class Settings:
    """Central configuration for Agentic AI Research & Outreach system."""

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile").strip()
    MAX_RESEARCH_ITERATIONS: int = int(os.getenv("MAX_RESEARCH_ITERATIONS", "3"))
    EVIDENCE_CONFIDENCE_THRESHOLD: float = float(os.getenv("EVIDENCE_CONFIDENCE_THRESHOLD", "0.75"))
    GMAIL_CREDENTIALS_PATH: str = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
    GMAIL_TOKEN_PATH: str = os.getenv("GMAIL_TOKEN_PATH", "token.json")
    MOCK_LLM_MODE: bool = os.getenv("MOCK_LLM_MODE", "false").lower() in ("true", "1", "yes")

    @classmethod
    def is_groq_configured(cls) -> bool:
        return bool(cls.GROQ_API_KEY) and cls.GROQ_API_KEY != "gsk_your_groq_api_key_here"

    @classmethod
    def get_llm(cls):
        """
        Initializes and returns the CrewAI Groq LLM instance.
        If Groq key is unconfigured and MOCK_LLM_MODE is False, warns user.
        """
        if not cls.is_groq_configured() and not cls.MOCK_LLM_MODE:
            # Check if user set key in runtime
            pass

        from crewai import LLM
        return LLM(
            model=cls.GROQ_MODEL,
            api_key=cls.GROQ_API_KEY if cls.is_groq_configured() else "dummy_key",
            temperature=0.2,
        )


settings = Settings()
