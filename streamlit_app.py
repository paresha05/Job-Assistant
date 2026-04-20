import streamlit as st
import logging
from orchestrator import run_pipeline
from usajobs_api import fetch_usajobs
from utils.tracking import get_applications_summary
from utils.resume_parser import parse_resume, check_resume_relevance
from utils.config import get_llm_string

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

# Resume upload
st.markdown("#### Upload Your Resume")
uploaded_file = st.file_uploader(
    "Upload resume (.pdf or .docx, max 5 MB)",
    type=["pdf", "docx"],
    help="Your resume will be parsed and matched against selected job descriptions."
)

resume_text = ""
if uploaded_file is not None:
    with st.spinner("Parsing resume..."):
        text, error = parse_resume(uploaded_file)
    if error:
        st.error(f"Resume upload failed: {error}")
    else:
        resume_text = text
        st.success(f"Resume parsed successfully ({len(resume_text)} characters).")
        with st.expander("Preview extracted text", expanded=False):
            st.text(resume_text[:1000] + ("..." if len(resume_text) > 1000 else ""))

user_bio = st.text_area(
    "Short Bio (for outreach tone)",
    "I'm a data professional passionate about public service.",
    height=100,
    help="Brief description of yourself for personalized outreach messages"
)

# Input validation hints
if not keyword.strip():
    st.error("Please enter a job keyword")
elif uploaded_file is None:
    st.warning("Please upload your resume to continue")
elif not resume_text:
    pass  # error already shown above from parse failure
elif not user_bio.strip():
    st.warning("Please enter a short bio for outreach messages")

search_ready = keyword.strip() and bool(resume_text) and user_bio.strip()

# Step 1: Search Jobs
if st.button("Search Jobs", disabled=not search_ready):
    with st.spinner("Searching jobs on USAJobs.gov..."):
        try:
            job_posts = fetch_usajobs(keyword, location, results_per_page=5)
            if not job_posts:
                st.error("No job postings found for this search. Try different keywords or location.")
            else:
                st.session_state["jobs"] = job_posts
                st.session_state["resume_text"] = resume_text
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

        with st.expander(f"{title} — {org}", expanded=False):
            job_summary = job_data.get('UserArea', {}).get('Details', {}).get('JobSummary', '')
            if not job_summary:
                job_summary = job_data.get('PositionDescription', 'No description available')

            st.write("**Job Summary:**")
            st.write(job_summary[:500] + "..." if len(job_summary) > 500 else job_summary)

            checkbox = st.checkbox("Apply to this position", key=f"job_{i}")
            if checkbox:
                selected_indexes.append(i)

    # Step 3: Apply to selected jobs
    if st.button("Apply to Selected Jobs", disabled=not selected_indexes):
        if not selected_indexes:
            st.warning("Please select at least one job.")
        else:
            saved_resume = st.session_state.get("resume_text", resume_text)
            llm = get_llm_string()
            progress_bar = st.progress(0)
            results_container = st.container()
            total = len(selected_indexes)

            for idx, i in enumerate(selected_indexes):
                job_data = st.session_state["jobs"][i]['MatchedObjectDescriptor']
                job_title = job_data.get('PositionTitle', 'Unknown Position')
                job_summary = job_data.get('UserArea', {}).get('Details', {}).get('JobSummary', '') \
                    or job_data.get('PositionDescription', '')

                progress_bar.progress((idx + 1) / total)

                with results_container:
                    st.markdown("---")
                    st.markdown(f"### {job_title}")

                # Relevance check
                with st.spinner(f"Checking resume relevance for: {job_title}..."):
                    try:
                        relevance = check_resume_relevance(saved_resume, job_summary, job_title, llm)
                        level = relevance["level"]
                        reason = relevance["reason"]
                    except Exception as e:
                        logger.error(f"Relevance check failed: {e}")
                        level, reason = "Unknown", "Could not determine relevance."

                with results_container:
                    color = {"High": "green", "Medium": "orange", "Low": "red"}.get(level, "gray")
                    st.markdown(
                        f"**Resume Match:** :{color}[{level}]  \n*{reason}*"
                    )
                    if level == "Low":
                        st.warning("Low relevance detected — you can still proceed, but consider tailoring your resume.")

                # Run pipeline
                with st.spinner(f"Processing application for: {job_title}..."):
                    try:
                        result = run_pipeline(job_data, saved_resume, user_bio)

                        with results_container:
                            if "Pipeline failed" in str(result):
                                st.error(f"Failed to process: {result}")
                            else:
                                st.success("Application processed successfully!")
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
                            st.error(error_msg)

            progress_bar.progress(1.0)
            st.success("All selected applications have been processed!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<small>AI Job Assistant - Powered by CrewAI and Groq</small>
</div>
""", unsafe_allow_html=True)
