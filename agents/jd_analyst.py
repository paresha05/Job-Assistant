import os
from crewai import Agent, Task
from utils.config import get_llm_string

llm = get_llm_string()

def get_jd_analyst_agent():
    """
    Create and return a Job Description Analyst agent
    
    Returns:
        Agent: Configured JD analyst agent
    """
    return Agent(
        role="Job Description Analyst",
        goal="Understand and summarize government job postings with focus on key requirements",
        backstory="You're an expert in job market analysis with deep knowledge of US federal job listings. You excel at identifying key skills, qualifications, and requirements from complex government job descriptions.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def create_jd_analysis_task(agent, jd):
    """
    Create a job description analysis task
    
    Args:
        agent: The JD analyst agent
        jd (str): Job description text
    
    Returns:
        Task: Configured analysis task
    """
    # Create dynamic output path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, "data", "jd_analysis_report.md")
    
    return Task(
        description=f"""
        Analyze the following USAJobs job posting and extract key information:
        
        **Your analysis should include:**
        1. **Role Summary**: A concise 2-3 sentence overview of the position
        2. **Key Responsibilities**: Main duties and responsibilities (bullet points)
        3. **Required Qualifications**: Must-have qualifications, education, experience
        4. **Preferred Skills**: Nice-to-have skills and competencies
        5. **Special Requirements**: Security clearance, certifications, etc.
        6. **Application Tips**: Insights on what the hiring manager likely values most
        
        **Job Description:**
        {jd}
        
        Focus on federal government context and terminology. Be thorough but concise.
        """,
        expected_output="A well-structured markdown report with clearly defined sections for Role Summary, Key Responsibilities, Required Qualifications, Preferred Skills, Special Requirements, and Application Tips.",
        agent=agent,
        output_file=output_path
    )