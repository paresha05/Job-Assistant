import csv
import os
import datetime
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_cover_letter_file(job_title, cover_letter, directory=None):
    """
    Save cover letter to file with proper error handling
    
    Args:
        job_title (str): Job title for filename
        cover_letter (str): Cover letter content
        directory (str): Directory to save file (optional)
    
    Returns:
        str: Path to saved file or None if failed
    """
    try:
        if directory is None:
            # Use dynamic path relative to project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            directory = os.path.join(project_root, "data", "cover_letters")
        
        # Sanitize job title for filename
        sanitized_title = re.sub(r'[\\/*?:"<>|\r\n]', "_", job_title.strip())
        if not sanitized_title:
            sanitized_title = "Unknown_Job"
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{sanitized_title}_{timestamp}.txt"
        filepath = os.path.join(directory, filename)
        
        # Save cover letter
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(cover_letter)
        
        logger.info(f"Cover letter saved: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving cover letter for job '{job_title}': {e}")
        return None

def log_application(job_title, agency, resume_summary, filepath=None):
    """
    Log application to CSV file with proper error handling
    
    Args:
        job_title (str): Job title
        agency (str): Agency name
        resume_summary (str): Resume summary
        filepath (str): Path to CSV file (optional)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if filepath is None:
            # Use dynamic path relative to project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            filepath = os.path.join(project_root, "data", "applications_log.csv")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(filepath)
        
        # Prepare data
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row_data = [
            job_title.strip() if job_title else "Unknown Job",
            agency.strip() if agency else "Unknown Agency",
            resume_summary.strip()[:150] if resume_summary else "No summary",
            timestamp
        ]
        
        # Write to CSV
        with open(filepath, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write headers if new file
            if not file_exists:
                writer.writerow(["Job Title", "Agency", "Resume Summary", "Date Applied"])
            
            writer.writerow(row_data)
        
        logger.info(f"Application logged: {job_title} at {agency}")
        return True
        
    except Exception as e:
        logger.error(f"Error logging application for job '{job_title}': {e}")
        return False

def get_applications_summary(filepath=None):
    """
    Get summary of all logged applications
    
    Args:
        filepath (str): Path to CSV file (optional)
    
    Returns:
        dict: Summary statistics or None if failed
    """
    try:
        if filepath is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            filepath = os.path.join(project_root, "data", "applications_log.csv")
        
        if not os.path.exists(filepath):
            return {"total_applications": 0, "message": "No applications logged yet"}
        
        with open(filepath, "r", encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            applications = list(reader)
        
        total = len(applications)
        agencies = set(app.get("Agency", "Unknown") for app in applications)
        
        return {
            "total_applications": total,
            "unique_agencies": len(agencies),
            "agencies": list(agencies),
            "last_application": applications[-1]["Date Applied"] if applications else "None"
        }
        
    except Exception as e:
        logger.error(f"Error getting applications summary: {e}")
        return None