import requests
import logging
from utils.config import USAJOBS_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_usajobs(keyword, location="remote", results_per_page=5):
    """
    Fetch jobs from USAJobs.gov API
    
    Args:
        keyword (str): Job search keyword
        location (str): Job location (default: "remote")
        results_per_page (int): Number of results to return (default: 5)
    
    Returns:
        list: List of job postings or empty list if error occurs
    """
    if not keyword.strip():
        logger.error("Keyword cannot be empty")
        return []
    
    headers = {
        'Host': 'data.usajobs.gov',
        'User-Agent': 'pareshauchdadiya05@gmail.com',   
        'Authorization-Key': USAJOBS_API_KEY
    }
    
    params = {
        'Keyword': keyword,
        'LocationName': location,
        'ResultsPerPage': min(results_per_page, 500)  # API limit
    }
    
    url = "https://data.usajobs.gov/api/search"
    
    try:
        logger.info(f"Searching jobs for keyword: {keyword}, location: {location}")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        search_result = data.get('SearchResult', {})
        job_items = search_result.get('SearchResultItems', [])
        
        logger.info(f"Found {len(job_items)} job postings")
        return job_items
        
    except requests.exceptions.Timeout:
        logger.error("Request timed out while fetching jobs")
        return []
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error occurred: {e}")
        return []
    except ValueError as e:
        logger.error(f"JSON decode error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        return []

if __name__ == "__main__":
    jobs = fetch_usajobs("Software Development", location="San Antonio", results_per_page=10)
    for job in jobs:
        title = job['MatchedObjectDescriptor']['PositionTitle']
        agency = job['MatchedObjectDescriptor']['OrganizationName']
        print(f"{title} at {agency}")