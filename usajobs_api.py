import re
import requests
import logging
from utils.config import USAJOBS_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common stop words to ignore during keyword matching
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "of", "for", "in", "to", "with",
    "at", "by", "on", "is", "as", "be", "it", "its", "are", "was",
    "were", "this", "that", "from", "has", "have", "not", "but"
}


def _score_job(job_item, keywords):
    """
    Score a job by how well its title and description match the keywords.

    Scoring:
      - Full phrase match in title    → 100
      - All keyword words in title    → 80
      - Some keyword words in title   → 40 * (matched / total)
      - Keyword words in description  → 10 * (matched / total)

    Returns a float score (higher = more relevant).
    """
    desc = job_item.get('MatchedObjectDescriptor', {})
    title = desc.get('PositionTitle', '').lower()
    summary = desc.get('UserArea', {}).get('Details', {}).get('JobSummary', '')
    if not summary:
        summary = desc.get('PositionDescription', '')
    summary = summary.lower()

    phrase = " ".join(keywords)
    if phrase in title:
        return 100.0

    title_matches = sum(1 for w in keywords if w in title)
    desc_matches = sum(1 for w in keywords if w in summary)
    total = len(keywords)

    if title_matches == total:
        return 80.0
    if title_matches > 0:
        return 40.0 * (title_matches / total)
    if desc_matches > 0:
        return 10.0 * (desc_matches / total)
    return 0.0


def _extract_keywords(keyword_string):
    """Tokenise keyword string, remove stop words, lowercase."""
    words = re.findall(r"[a-zA-Z]+", keyword_string.lower())
    filtered = [w for w in words if w not in _STOP_WORDS]
    return filtered if filtered else words  # fallback: keep all if everything filtered


def fetch_usajobs(keyword, location="remote", results_per_page=5):
    """
    Fetch jobs from USAJobs.gov API and return only relevant results,
    ranked by how closely the job title/description matches the keyword.

    Fetches up to 3× the requested count from the API, scores each result,
    and returns the top `results_per_page` relevant ones.
    """
    if not keyword.strip():
        logger.error("Keyword cannot be empty")
        return []

    # Normalise common "remote" variants to the USAJobs location value
    _remote_aliases = {"remote", "anywhere", "nationwide", "work from home", "wfh", "telework"}
    if location.strip().lower() in _remote_aliases:
        location = "Anywhere in the US"

    headers = {
        'Host': 'data.usajobs.gov',
        'User-Agent': 'pareshauchdadiya05@gmail.com',
        'Authorization-Key': USAJOBS_API_KEY
    }

    # Fetch more than needed so we have room to filter
    fetch_count = min(results_per_page * 3, 500)

    params = {
        'Keyword': keyword,
        'LocationName': location,
        'ResultsPerPage': fetch_count,
    }

    url = "https://data.usajobs.gov/api/search"

    try:
        logger.info(f"Searching jobs for keyword: {keyword}, location: {location}")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        job_items = data.get('SearchResult', {}).get('SearchResultItems', [])
        logger.info(f"API returned {len(job_items)} raw results")

        if not job_items:
            return []

        keywords = _extract_keywords(keyword)
        logger.info(f"Matching against keywords: {keywords}")

        # Score and filter
        scored = [(job, _score_job(job, keywords)) for job in job_items]
        relevant = [(job, score) for job, score in scored if score > 0]

        if not relevant:
            # No matches at all — fall back to top raw results
            logger.warning("No keyword-matched jobs found; returning top raw results")
            return job_items[:results_per_page]

        # Sort by score descending
        relevant.sort(key=lambda x: x[1], reverse=True)

        # Prefer jobs where all keyword words appear in the title (score >= 40).
        # Only fall back to partial matches if there are fewer than requested.
        high_quality = [(job, score) for job, score in relevant if score >= 40]
        if high_quality:
            top_jobs = [job for job, _ in high_quality[:results_per_page]]
        else:
            # No strong title match — use any partial match
            top_jobs = [job for job, _ in relevant[:results_per_page]]

        logger.info(f"Returning {len(top_jobs)} relevant job(s) after keyword filtering")
        return top_jobs

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