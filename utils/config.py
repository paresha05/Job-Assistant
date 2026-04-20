import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# API Keys
USAJOBS_API_KEY = os.getenv("USAJOBS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_available_llm_config():
    if GROQ_API_KEY:
        return ("groq", GROQ_API_KEY, "llama-3.3-70b-versatile")
    elif OPENAI_API_KEY:
        return ("openai", OPENAI_API_KEY, "gpt-3.5-turbo")
    elif ANTHROPIC_API_KEY:
        return ("anthropic", ANTHROPIC_API_KEY, "claude-3-haiku-20240307")
    elif GEMINI_API_KEY:
        return ("gemini", GEMINI_API_KEY, "gemini-1.5-flash")
    else:
        raise ValueError("No LLM API key found. Please set GROQ_API_KEY or another provider key.")

def get_llm_string():
    """Return a crewai.LLM instance for use with CrewAI v1.x agents."""
    from crewai.llm import LLM
    provider, api_key, model = get_available_llm_config()
    key_map = {"groq": "GROQ_API_KEY", "openai": "OPENAI_API_KEY",
               "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}
    prefix = {"groq": "groq/", "openai": "", "anthropic": "anthropic/", "gemini": "gemini/"}
    os.environ[key_map[provider]] = api_key
    return LLM(model=f"{prefix[provider]}{model}")

if not USAJOBS_API_KEY:
    print("Warning: USAJOBS_API_KEY not set - job search features will be limited")