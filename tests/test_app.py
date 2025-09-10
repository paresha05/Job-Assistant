#!/usr/bin/env python3
"""
Test script for Job Hunt Assistant
Run this to test the application functionality
"""

import os
import sys
import requests
import time

def test_web_interface():
    """Test if the Streamlit web interface is accessible"""
    print("🌐 Testing Web Interface...")
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            print("✅ Web interface is accessible!")
            print(f"📊 Response status: {response.status_code}")
            return True
        else:
            print(f"❌ Web interface returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to web interface: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n📦 Testing Python Imports...")
    
    modules_to_test = [
        "streamlit",
        "crewai", 
        "openai",
        "pandas",
        "requests",
        "os",
        "json"
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {failed_imports}")
        return False
    else:
        print("\n✅ All imports successful!")
        return True

def test_file_structure():
    """Test if required files and directories exist"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "streamlit_app.py",
        "orchestrator.py", 
        "usajobs_api.py",
        "requirements.txt",
        "agents/jd_analyst.py",
        "agents/resume_cl_agent.py",
        "agents/messaging_agent.py",
        "utils/config.py",
        "utils/tracking.py"
    ]
    
    required_dirs = [
        "data",
        "data/cover_letters",
        "agents",
        "utils"
    ]
    
    missing_files = []
    missing_dirs = []
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/")
            missing_dirs.append(dir_path)
    
    if missing_files or missing_dirs:
        print(f"\n❌ Missing files: {missing_files}")
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("\n✅ All required files and directories exist!")
        return True

def test_environment_setup():
    """Test environment configuration"""
    print("\n🔧 Testing Environment Setup...")
    
    # Check for API keys (optional but recommended)
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "USAJOBS_API_KEY": os.getenv("USAJOBS_API_KEY"),
        "USAJOBS_USER_AGENT": os.getenv("USAJOBS_USER_AGENT")
    }
    
    configured_keys = []
    missing_keys = []
    
    for key, value in api_keys.items():
        if value:
            print(f"✅ {key}: Configured")
            configured_keys.append(key)
        else:
            print(f"⚠️  {key}: Not set")
            missing_keys.append(key)
    
    if missing_keys:
        print(f"\n⚠️  Note: {len(missing_keys)} API keys not configured.")
        print("   This is normal for initial testing, but required for full functionality.")
        print("   Missing keys:", missing_keys)
    
    return True

def main():
    """Run all tests"""
    print("🧪 Job Hunt Assistant - Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Imports", test_imports),
        ("Environment Setup", test_environment_setup),
        ("Web Interface", test_web_interface)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your application is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Keep the app running and visit: http://localhost:8501")
        print("   2. Set up API keys for full functionality")
        print("   3. Upload a resume and start job hunting!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
