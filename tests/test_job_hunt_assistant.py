"""
Basic tests for the Job Hunt Assistant application
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

class TestUSAJobsAPI(unittest.TestCase):
    """Test cases for USAJobs API functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_keyword = "business analyst"
        self.test_location = "New York"
    
    @patch('usajobs_api.requests.get')
    def test_fetch_usajobs_success(self, mock_get):
        """Test successful job fetch from USAJobs API"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'SearchResult': {
                'SearchResultItems': [
                    {
                        'MatchedObjectDescriptor': {
                            'PositionTitle': 'Test Job',
                            'OrganizationName': 'Test Agency'
                        }
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        from usajobs_api import fetch_usajobs
        result = fetch_usajobs(self.test_keyword, self.test_location)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['MatchedObjectDescriptor']['PositionTitle'], 'Test Job')
    
    @patch('usajobs_api.requests.get')
    def test_fetch_usajobs_empty_keyword(self, mock_get):
        """Test fetch with empty keyword"""
        from usajobs_api import fetch_usajobs
        result = fetch_usajobs("")
        
        self.assertEqual(result, [])
        mock_get.assert_not_called()


class TestTracking(unittest.TestCase):
    """Test cases for application tracking functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_job_title = "Test Job Title"
        self.test_agency = "Test Agency"
        self.test_resume_summary = "Test resume summary"
        self.test_cover_letter = "Test cover letter content"
    
    def test_log_application(self):
        """Test application logging functionality"""
        from utils.tracking import log_application
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            result = log_application(
                self.test_job_title, 
                self.test_agency, 
                self.test_resume_summary, 
                filepath=tmp_path
            )
            self.assertTrue(result)
            self.assertTrue(os.path.exists(tmp_path))
            
            # Read and verify content
            with open(tmp_path, 'r') as f:
                content = f.read()
                self.assertIn(self.test_job_title, content)
                self.assertIn(self.test_agency, content)
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_save_cover_letter_file(self):
        """Test cover letter file saving"""
        from utils.tracking import save_cover_letter_file
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = save_cover_letter_file(
                self.test_job_title,
                self.test_cover_letter,
                directory=tmp_dir
            )
            
            self.assertIsNotNone(result)
            self.assertTrue(os.path.exists(result))
            
            with open(result, 'r') as f:
                content = f.read()
                self.assertEqual(content, self.test_cover_letter)


class TestOrchestrator(unittest.TestCase):
    """Test cases for the main orchestrator"""
    
    def test_extract_between_markers(self):
        """Test text extraction between markers"""
        from orchestrator import extract_between_markers
        
        test_text = "Some text <<START>>extracted content<<END>> more text"
        result = extract_between_markers(test_text, "<<START>>", "<<END>>")
        self.assertEqual(result, "extracted content")
        
        # Test with missing marker
        result = extract_between_markers(test_text, "<<MISSING>>", "<<END>>")
        self.assertEqual(result, "Not found")
    
    def test_load_resume_file_not_found(self):
        """Test loading resume with non-existent file"""
        from orchestrator import load_resume
        
        result = load_resume("/nonexistent/path/resume.txt")
        self.assertEqual(result, "")


class TestConfigValidation(unittest.TestCase):
    """Test cases for configuration validation"""
    
    def test_config_validation(self):
        """Test that config validation works"""
        # This test will fail if environment variables are not set
        try:
            from utils.config import USAJOBS_API_KEY, GEMINI_API_KEY
            self.assertIsNotNone(USAJOBS_API_KEY)
            self.assertIsNotNone(GEMINI_API_KEY)
        except ValueError as e:
            self.skipTest(f"Environment variables not configured: {e}")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
