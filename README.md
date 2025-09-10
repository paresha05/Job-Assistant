# AI Job Hunt Assistant

An intelligent job hunting assistant that uses AI agents to automate the federal government job application process. The system searches USAJobs.gov, analyzes job descriptions, tailors resumes, generates cover letters, and creates personalized outreach messages.

## Features

- 🔍 **Job Search**: Search USAJobs.gov with keywords and location filters
- 🤖 **AI Agents**: Three specialized AI agents for comprehensive job application support
  - **JD Analyst**: Analyzes job descriptions and extracts key requirements
  - **Resume/CL Agent**: Tailors resume summaries and generates cover letters
  - **Messaging Agent**: Creates professional outreach messages
- 📊 **Application Tracking**: Automatic logging of applications with CSV export
- 💾 **File Management**: Organized storage of cover letters and outputs
- 🖥️ **Web Interface**: User-friendly Streamlit interface

## Architecture

```
job-hunt-assistant/
├── orchestrator.py          # Main pipeline orchestrator
├── streamlit_app.py         # Web interface
├── usajobs_api.py          # USAJobs API integration
├── agents/                 # AI agents
│   ├── jd_analyst.py       # Job description analyzer
│   ├── resume_cl_agent.py  # Resume & cover letter writer
│   └── messaging_agent.py  # Outreach message writer
├── utils/                  # Utilities
│   ├── config.py           # Configuration management
│   └── tracking.py         # Application tracking
└── data/                   # Data storage
    ├── sample_resume.txt   # Sample resume
    ├── applications_log.csv # Application log
    └── cover_letters/      # Generated cover letters
```

## Installation

### Option 1: Docker Deployment (Recommended)

#### Quick Start
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd job-hunt-assistant
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.template .env
   # Edit .env and add your API keys
   ```

3. **Deploy with Docker**:
   ```bash
   # Development mode
   ./dev-deploy.sh
   
   # Or production mode
   ./deploy.sh
   ```

4. **Access the application**: http://yourhost

#### Docker Commands
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose build --no-cache
```

#### Production Deployment
```bash
# With nginx reverse proxy
./prod-deploy.sh

# Access at http://localhost (port 80)
```

### Option 2: Local Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd job-hunt-assistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   USAJOBS_API_KEY=your_usajobs_api_key
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

## Getting API Keys

### USAJobs API Key
1. Visit [USAJobs API](https://developer.usajobs.gov/APIRequest/Index)
2. Request an API key
3. Add it to your `.env` file

### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## Usage

### Docker Usage (Recommended)
```bash
# Start the application
./deploy.sh

# Or for development with hot reload
./dev-deploy.sh

# Access at http://localhost:8501
```

### Web Interface (Local)
```bash
streamlit run streamlit_app.py
```

### Command Line
```python
from orchestrator import run_pipeline
from usajobs_api import fetch_usajobs

# Search jobs
jobs = fetch_usajobs("business analyst", "New York")

# Process a job
if jobs:
    job_data = jobs[0]['MatchedObjectDescriptor']
    resume_text = "Your resume content..."
    user_bio = "Your bio for outreach..."
    result = run_pipeline(job_data, resume_text, user_bio)
```

## Docker Architecture

The application is containerized with the following components:

- **Main App Container**: Runs Streamlit application
- **Nginx Container** (Production): Reverse proxy with SSL support
- **Persistent Volumes**: For data storage and logs
- **Health Checks**: Automatic service monitoring

### Environment Variables
- `USAJOBS_API_KEY`: Your USAJobs.gov API key
- `GEMINI_API_KEY`: Your Google Gemini API key

### Ports
- **8501**: Streamlit application (development)
- **80**: Nginx reverse proxy (production)
- **443**: HTTPS (production with SSL)

## Configuration

The system uses environment variables for configuration:

- `USAJOBS_API_KEY`: Your USAJobs.gov API key
- `GEMINI_API_KEY`: Your Google Gemini API key

## Output Files

- **Applications Log**: `data/applications_log.csv` - CSV log of all applications
- **Cover Letters**: `data/cover_letters/` - Individual cover letter files
- **Agent Outputs**: `data/resume_agent_output.txt` - Detailed agent outputs

## AI Agents

### JD Analyst Agent
- Analyzes job descriptions
- Extracts key skills and qualifications
- Creates structured summaries

### Resume/CL Agent
- Tailors resume summaries to job requirements
- Generates personalized cover letters
- Optimizes for government positions

### Messaging Agent
- Creates professional outreach messages
- Keeps messages concise (under 150 words)
- Tailors tone for LinkedIn/email platforms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please open an issue on GitHub 