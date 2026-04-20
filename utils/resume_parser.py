import io


MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = [".pdf", ".docx"]


def validate_file(uploaded_file):
    """
    Validate uploaded resume file.
    Returns (is_valid, error_message)
    """
    import os
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Please upload a .pdf or .docx file."

    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File is too large ({size_mb:.1f} MB). Maximum allowed size is {MAX_FILE_SIZE_MB} MB."

    return True, None


def extract_text_from_pdf(file_bytes):
    import pdfplumber
    text = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text).strip()


def extract_text_from_docx(file_bytes):
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def parse_resume(uploaded_file):
    """
    Parse resume from uploaded Streamlit file object.
    Returns (text, error_message). On failure text is None.
    """
    import os
    is_valid, error = validate_file(uploaded_file)
    if not is_valid:
        return None, error

    file_bytes = uploaded_file.read()
    if not file_bytes:
        return None, "Uploaded file appears to be empty."

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    try:
        if ext == ".pdf":
            text = extract_text_from_pdf(file_bytes)
        else:
            text = extract_text_from_docx(file_bytes)
    except Exception as e:
        return None, f"Failed to parse file: {e}"

    if not text:
        return None, "Could not extract any text from the file. The file may be scanned/image-based."

    return text, None


def check_resume_relevance(resume_text, job_summary, job_title, llm_string):
    """
    Use the LLM to check how relevant the resume is for the job.
    Returns dict with keys: level (High/Medium/Low), reason (str)
    """
    from crewai.llm import LLM

    llm = llm_string if isinstance(llm_string, LLM) else LLM(model=llm_string)

    prompt = f"""You are a resume screener. Given the resume and job description below, rate how relevant the resume is for the job.

Job Title: {job_title}

Job Description:
{job_summary[:1500]}

Resume (first 1500 chars):
{resume_text[:1500]}

Respond in this exact format (2 lines only):
Level: <High|Medium|Low>
Reason: <one sentence explaining the match>"""

    response = llm.call([{"role": "user", "content": prompt}])
    response_text = response if isinstance(response, str) else str(response)

    level = "Medium"
    reason = "Could not determine relevance."
    for line in response_text.splitlines():
        if line.startswith("Level:"):
            val = line.replace("Level:", "").strip()
            if val in ("High", "Medium", "Low"):
                level = val
        elif line.startswith("Reason:"):
            reason = line.replace("Reason:", "").strip()

    return {"level": level, "reason": reason}
