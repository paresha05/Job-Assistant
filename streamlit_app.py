import streamlit as st
import logging
from orchestrator import run_pipeline
from usajobs_api import fetch_usajobs
from utils.tracking import get_applications_summary

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AI Job Assistant", 
    layout="centered",
    page_icon="🤖"
)

st.title(" AI Job Assistant")
st.markdown("""
Use AI agents to analyze jobs, tailor your resume, and write outreach messages — all from one interface.
*Specifically designed for USAJobs.gov federal positions.*
""")

# Sidebar with application summary
with st.sidebar:
    st.header("Application Summary")
    try:
        summary = get_applications_summary()
        if summary:
            st.metric("Total Applications", summary.get("total_applications", 0))
            st.metric("Unique Agencies", summary.get("unique_agencies", 0))
            if summary.get("last_application"):
                st.write(f"**Last Applied:** {summary['last_application']}")
        else:
            st.info("No applications logged yet")
    except Exception as e:
        st.error("Error loading application summary")
        logger.error(f"Error in sidebar summary: {e}")

# Main interface
col1, col2 = st.columns(2)
with col1:
    keyword = st.text_input("Job Keyword", "business analyst", help="Enter keywords to search for jobs")
with col2:
    location = st.text_input("Location", "New York", help="Enter location or 'remote'")

resume_text = st.text_area(
    "Paste Your Resume", 
    height=200, 
    help="Paste your complete resume text here"
)

user_bio = st.text_area(
    "Short Bio (for outreach tone)", 
    "I'm a data professional passionate about public service.",
    height=100,
    help="Brief description of yourself for personalized outreach messages"
)

# Input validation
if not keyword.strip():
    st.error("Please enter a job keyword")
elif not resume_text.strip():
    st.warning("Please paste your resume to continue")
elif not user_bio.strip():
    st.warning("Please enter a short bio for outreach messages")

# Step 1: Search Jobs
if st.button(" Search Jobs", disabled=not (keyword.strip() and resume_text.strip() and user_bio.strip())):
    with st.spinner("Searching jobs on USAJobs.gov..."):
        try:
            job_posts = fetch_usajobs(keyword, location, results_per_page=5)
            if not job_posts:
                st.error("No job postings found for this search. Try different keywords or location.")
            else:
                st.session_state["jobs"] = job_posts
                st.success(f"Found {len(job_posts)} job postings! Select the ones you'd like to apply for.")
        except Exception as e:
            st.error(f"Error searching for jobs: {str(e)}")
            logger.error(f"Job search error: {e}")

# Step 2: Show checkbox list for job selection
if "jobs" in st.session_state:
    selected_indexes = []
    st.markdown("### Select Jobs to Apply For:")
    
    for i, job in enumerate(st.session_state["jobs"]):
        job_data = job['MatchedObjectDescriptor']
        title = job_data.get('PositionTitle', 'Unknown Title')
        org = job_data.get('OrganizationName', 'Unknown Agency')
        
        # Create expandable job details
        with st.expander(f"{title} — {org}", expanded=False):
            # Show job details if available
            job_summary = job_data.get('UserArea', {}).get('Details', {}).get('JobSummary', '')
            if not job_summary:
                job_summary = job_data.get('PositionDescription', 'No description available')
            
            st.write("**Job Summary:**")
            st.write(job_summary[:500] + "..." if len(job_summary) > 500 else job_summary)
            
            # Checkbox for selection
            checkbox = st.checkbox(f"Apply to this position", key=f"job_{i}")
            if checkbox:
                selected_indexes.append(i)

    # Step 3: Apply to selected jobs
    if st.button(" Apply to Selected Jobs", disabled=not selected_indexes):
        if not selected_indexes:
            st.warning("Please select at least one job.")
        else:
            progress_bar = st.progress(0)
            results_container = st.container()
            
            for idx, i in enumerate(selected_indexes):
                job_data = st.session_state["jobs"][i]['MatchedObjectDescriptor']
                job_title = job_data.get('PositionTitle', 'Unknown Position')
                
                # Update progress
                progress_bar.progress((idx + 1) / len(selected_indexes))
                
                with st.spinner(f"Processing application for: {job_title}"):
                    try:
                        result = run_pipeline(job_data, resume_text, user_bio)
                        
                        with results_container:
                            st.markdown("---")
                            st.markdown(f"###  Outreach Message for: {job_title}")
                            
                            # Display result in a nice format
                            if "Pipeline failed" in str(result):
                                st.error(f" Failed to process: {result}")
                            else:
                                st.success(" Application processed successfully!")
                                st.markdown("**Generated Outreach Message:**")
                                st.text_area(
                                    f"Message for {job_title}", 
                                    value=str(result), 
                                    height=150,
                                    key=f"message_{i}"
                                )
                    
                    except Exception as e:
                        error_msg = f"Error processing {job_title}: {str(e)}"
                        logger.error(error_msg)
                        with results_container:
                            st.error(f"{error_msg}")
            
            progress_bar.progress(1.0)
            st.success(" All selected applications have been processed!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<small>AI Job Assistant - Powered by CrewAI and Google Gemini</small>
</div>
""", unsafe_allow_html=True)
