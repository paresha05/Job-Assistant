import os
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# API Keys
USAJOBS_API_KEY = os.getenv("USAJOBS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# LLM Configuration - Use available provider
def get_available_llm_config():
    """
    Determine which LLM provider to use based on available API keys
    Returns tuple of (provider_name, api_key, model_name)
    """
    if OPENAI_API_KEY:
        return ("openai", OPENAI_API_KEY, "gpt-3.5-turbo")
    elif ANTHROPIC_API_KEY:
        return ("anthropic", ANTHROPIC_API_KEY, "claude-3-haiku-20240307")
    elif GEMINI_API_KEY:
        return ("gemini", GEMINI_API_KEY, "gemini-1.5-flash")
    else:
        raise ValueError("No LLM API key found. Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY")

# Validate required environment variables
if not USAJOBS_API_KEY:
    print("Warning: USAJOBS_API_KEY not set - job search features will be limited")