# Manual Testing Checklist for Job Hunt Assistant

## 🧪 Testing Steps

### **1. Basic Functionality Test**

**Status:** ⬜ Not Started / 🔄 In Progress / ✅ Passed / ❌ Failed

#### A. Application Startup
- ⬜ Run: `docker run -p 8501:8501 job-hunt-test streamlit run streamlit_app.py --server.address=0.0.0.0`  
- ⬜ Open browser: `http://localhost:8501`
- ⬜ Check: Homepage loads without errors
- ⬜ Check: No Python error messages in browser

#### B. User Interface Test
- ⬜ **Navigation:** Sidebar shows all sections
- ⬜ **Job Search:** Job search form is visible  
- ⬜ **Resume Upload:** File upload widget works
- ⬜ **Settings:** Configuration section accessible

#### C. File Upload Test (No API keys needed)
- ⬜ Try uploading a text/PDF file in resume section
- ⬜ Check: File upload doesn't crash the app
- ⬜ Check: Some feedback message appears

### **2. Core Components Test** 

#### A. Job Data Input
- ⬜ Enter sample job details in the job search form
- ⬜ Company name, job title, description fields work
- ⬜ Form validation works (required fields)

#### B. Resume Processing  
- ⬜ Upload a sample resume file
- ⬜ App processes file without crashing
- ⬜ Some text extraction occurs (even if limited)

#### C. Error Handling
- ⬜ Try submitting empty forms
- ⬜ Check app shows appropriate error messages
- ⬜ App doesn't crash on invalid input

### **3. API Integration Test (Requires API Keys)**

#### A. With Valid API Keys
- ⬜ Set environment variables for API keys
- ⬜ Run: `docker run -e OPENAI_API_KEY=your_key -p 8501:8501 job-hunt-test ...`
- ⬜ Test full job analysis workflow
- ⬜ Test cover letter generation  
- ⬜ Test resume tailoring

#### B. Expected Results (with API keys)
- ⬜ Job description analysis completes
- ⬜ Cover letter generates successfully  
- ⬜ Resume suggestions appear
- ⬜ Application tracking updates

### **4. Data Persistence Test**

#### A. File System  
- ⬜ Check `data/` folder gets created
- ⬜ Check `data/cover_letters/` gets populated
- ⬜ Check `data/applications_log.csv` updates
- ⬜ Check log files are created

### **5. Performance Test**

#### A. Resource Usage
- ⬜ App starts within 10 seconds  
- ⬜ Memory usage reasonable (<2GB)
- ⬜ No memory leaks during normal use
- ⬜ Response time acceptable for UI interactions

## 🚨 Common Issues & Solutions

### Issue: "Module not found" errors
**Solution:** Rebuild Docker image: `docker build -f Dockerfile.simple -t job-hunt-test .`

### Issue: "Connection refused" on localhost:8501  
**Solution:** Check Docker port mapping: `-p 8501:8501`

### Issue: API key errors
**Solution:** Expected without keys - add environment variables for full functionality

### Issue: File upload fails
**Solution:** Check file permissions and supported formats

## 📝 Test Results Summary

Date: ___________
Tester: ___________

**Basic Functionality:** ⬜ Pass ⬜ Fail  
**User Interface:** ⬜ Pass ⬜ Fail  
**Error Handling:** ⬜ Pass ⬜ Fail  
**File Operations:** ⬜ Pass ⬜ Fail  

**Overall Status:** ⬜ Ready for Use ⬜ Needs Fixes

**Notes:**
_________________________________
_________________________________
_________________________________

## 🎯 Success Criteria

✅ **Minimum for "Working":**
- App starts and loads in browser
- No Python crashes or exceptions  
- Basic UI elements are functional
- File uploads don't break the app

✅ **Full Functionality:**
- All above PLUS valid API keys
- Successful job analysis
- Cover letter generation works  
- Resume tailoring completes
- Data saves correctly
