# Testing with API Keys

## Set up environment variables (replace with your actual keys):

export OPENAI_API_KEY="your-openai-key-here"
export ANTHROPIC_API_KEY="your-anthropic-key-here"  
export USAJOBS_API_KEY="your-usajobs-key-here"
export USAJOBS_USER_AGENT="YourName-JobHuntAssistant/1.0"

## Then run with API keys:

docker run --rm \
  -p 8501:8501 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e USAJOBS_API_KEY="$USAJOBS_API_KEY" \
  -e USAJOBS_USER_AGENT="$USAJOBS_USER_AGENT" \
  job-hunt-test \
  streamlit run streamlit_app.py --server.address=0.0.0.0

## Test the full workflow:
1. Upload your resume
2. Search for jobs or paste job description  
3. Generate tailored cover letter
4. Review AI suggestions
5. Track applications
