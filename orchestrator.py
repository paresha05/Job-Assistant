import os
import logging
from crewai import Crew, Process
from agents.jd_analyst import get_jd_analyst_agent,create_jd_analysis_task
from usajobs_api import fetch_usajobs
from agents.resume_cl_agent import get_resume_cl_agent, create_resume_cl_task
from agents.messaging_agent import get_messaging_agent, create_messaging_task
from utils.tracking import log_application, save_cover_letter_file

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_between_markers(text, start, end=None):
    """
    Extract text between specified markers
    
    Args:
        text (str): Text to search in
        start (str): Start marker
        end (str): End marker (optional)
    
    Returns:
        str: Extracted text or "Not found" if markers not found
    """
    try:
        start_idx = text.index(start) + len(start)
        end_idx = text.index(end, start_idx) if end else len(text)
        return text[start_idx:end_idx].strip()
    except ValueError:
        logger.warning(f"Markers not found in text: start='{start}', end='{end}'")
        return "Not found"

def load_resume(path=None):
    """
    Load resume from file
    
    Args:
        path (str): Path to resume file (optional)
    
    Returns:
        str: Resume content or empty string if file not found
    """
    if path is None:
        # Use dynamic path relative to project root
        project_root = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(project_root, "data", "sample_resume.txt")
    
    try:
        with open(path, "r", encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Resume file not found: {path}")
        return ""
    except Exception as e:
        logger.error(f"Error reading resume file: {e}")
        return ""


def run_pipeline(job_data, resume_text, user_bio):
    """
    Run the complete job application pipeline
    
    Args:
        job_data (dict): Job information from USAJobs API
        resume_text (str): User's resume content
        user_bio (str): User's bio for outreach messages
    
    Returns:
        str: Final pipeline result or error message
    """
    try:
        # Extract job information with fallbacks
        job_summary = job_data.get('UserArea', {}).get('Details', {}).get('JobSummary', '')
        if not job_summary:
            job_summary = job_data.get('PositionDescription', 'No job summary available')
        
        agency_name = job_data.get('OrganizationName', 'Unknown Agency')
        job_title = job_data.get('PositionTitle', 'Unknown Position')

        logger.info(f"Processing job: {job_title} at {agency_name}")

        # Validate inputs
        if not resume_text.strip():
            raise ValueError("Resume text cannot be empty")
        if not user_bio.strip():
            raise ValueError("User bio cannot be empty")

        # Initialize agents
        logger.info("Initializing AI agents...")
        jd_agent = get_jd_analyst_agent()
        resume_agent = get_resume_cl_agent()
        message_agent = get_messaging_agent()

        # Create tasks
        logger.info("Creating tasks...")
        jd_task = create_jd_analysis_task(jd_agent, job_summary)
        resume_task = create_resume_cl_task(resume_agent, job_summary, resume_text)
        message_task = create_messaging_task(message_agent, job_summary, agency_name, user_bio)

        # Run the crew
        logger.info("Running AI agent crew...")
        crew = Crew(
            agents=[jd_agent, resume_agent, message_agent],
            tasks=[jd_task, resume_task, message_task],
            process=Process.sequential
        )
        result = crew.kickoff()

        logger.info("Pipeline completed successfully")
        print("\n=== FINAL OUTPUT ===\n")
        print(result)

        # Extract key outputs
        resume_output = str(resume_task.output)
        resume_summary = extract_between_markers(resume_output, "<<RESUME_SUMMARY>>", "<<COVER_LETTER>>")
        cover_letter = extract_between_markers(resume_output, "<<COVER_LETTER>>")

        # Log and save with error handling
        try:
            log_application(job_title, agency_name, resume_summary)
            save_cover_letter_file(job_title, cover_letter)
            logger.info("Application logged and cover letter saved successfully")
        except Exception as e:
            logger.error(f"Error saving application data: {e}")

        return str(result)
    
    except Exception as e:
        error_msg = f"Pipeline failed for job '{job_title}': {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__=="__main__":
    run_pipeline()
