import os
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

# Initialize LLM
llm = get_llm()

def get_resume_cl_agent():
    """
    Create and return a Resume and Cover Letter agent
    
    Returns:
        Agent: Configured resume/cover letter agent
    """
    return Agent(
        role="Resume and Cover Letter Specialist",
        goal="Customize application materials to perfectly match job descriptions and maximize application success.",
        backstory="You're an expert career counselor and professional writer with extensive experience in government and tech recruitment. You understand what hiring managers look for and how to tailor resumes and cover letters for maximum impact, especially for federal positions.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def create_resume_cl_task(agent, job_summary, resume_content):
    """
    Create a resume and cover letter customization task
    
    Args:
        agent: The resume/cover letter agent
        job_summary (str): Job description/summary
        resume_content (str): Original resume content
    
    Returns:
        Task: Configured customization task
    """
    # Create dynamic output path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, "data", "resume_agent_output.txt")
    
    return Task(
        description=f"""
        Based on the job summary below, customize the candidate's resume summary and generate a personalized cover letter that will stand out to hiring managers.
        
        **Job Summary:**
        {job_summary}
        
        **Current Resume:**
        {resume_content}
        
        **Your tasks:**
        1. **Tailored Resume Summary**: Create a compelling 3-5 sentence professional summary that aligns the candidate's experience with the job requirements. Highlight relevant skills and experiences that match the posting.
        
        2. **Personalized Cover Letter**: Write a professional, engaging cover letter (300-400 words) that:
           - Opens with enthusiasm for the specific position and agency
           - Demonstrates understanding of the role and its requirements
           - Highlights 2-3 key qualifications that make the candidate ideal
           - Shows knowledge of the agency's mission (if mentioned)
           - Closes with a strong call to action
           - Uses professional government job application tone
        
        **Important:** Use specific keywords from the job posting and quantify achievements where possible.
        """,
        agent=agent,
        expected_output="""
        <<RESUME_SUMMARY>>
        [Your tailored 3-5 sentence resume summary that aligns with the job requirements, incorporating relevant keywords and highlighting matching qualifications]

        <<COVER_LETTER>>
        [Your personalized, professional cover letter (300-400 words) formatted for a government job application, demonstrating clear understanding of the role and enthusiasm for the position]
        """,
        output_file=output_path
    )   