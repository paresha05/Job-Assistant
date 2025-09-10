from crewai import Agent, Task
from utils.config import get_available_llm_config

# Initialize LLM with error handling and flexible provider support
def get_llm():
    """Initialize LLM based on available API keys"""
    try:
        provider, api_key, model_name = get_available_llm_config()
        
        if provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model_name,
                temperature=0.1,
                openai_api_key=api_key
            )
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=model_name,
                temperature=0.1,
                anthropic_api_key=api_key
            )
        elif provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.1,
                google_api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
            
    except Exception as e:
        raise RuntimeError(f"Failed to initialize LLM: {e}")

llm = get_llm()

def get_messaging_agent():
    return Agent(
        role="Outreach Message Writer",
        goal="Draft personalized messages for job outreach",
        backstory="You're a professional career coach skilled in writing effective cold emails and outreach messages for job seekers in tech and government.",
        llm=llm,
        verbose=True
    )

def create_messaging_task(agent,JobSummary,agency_name,user_bio):
    return Task(
         description=f"""
        Write a concise and compelling outreach message that the candidate could send to someone at {agency_name}, expressing interest in the job described below.
        
        --- Job Summary ---
        {JobSummary}
        
        --- Candidate Bio ---
        {user_bio}
        
        The message should be friendly, professional, and under 150 words. Tailor it for a platform like LinkedIn or email.
        """,
        expected_output="A short outreach message under 150 words, tailored for LinkedIn or email, that is professional and expresses interest in the job at the given agency.",
        agent=agent
    )