#!/usr/bin/env python3
"""
Quick backend verification script.
Tests the backend API without requiring real LLM keys.
"""
import json
import requests
import sys
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        print("✓ Health check passed")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_providers():
    """Test providers info endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/providers", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "preferred_provider" in data
        print(f"✓ Providers endpoint works")
        print(f"  Preferred provider: {data.get('preferred_provider')}")
        print(f"  Gemini configured: {data.get('gemini_configured')}")
        print(f"  Groq configured: {data.get('groq_configured')}")
        print(f"  OpenAI configured: {data.get('openai_configured')}")
        return True
    except Exception as e:
        print(f"✗ Providers check failed: {e}")
        return False

def test_analyze_no_keys():
    """Test analyze endpoint without keys (should fail gracefully)"""
    try:
        payload = {
            "transcript": "The candidate has 10 years of backend experience with Java and Python."
        }
        r = requests.post(f"{BASE_URL}/api/analyze", json=payload, timeout=5)
        # Should return 400 with helpful message
        assert r.status_code == 400
        data = r.json()
        assert "All providers failed" in data.get("detail", "")
        print("✓ Analyze endpoint error handling works (no keys configured)")
        return True
    except Exception as e:
        print(f"✗ Analyze test failed: {e}")
        return False

def main():
    print("Testing AI Interview Analyzer Backend")
    print("=" * 50)
    
    # Check if backend is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except Exception:
        print(f"✗ Backend not running on {BASE_URL}")
        print("  Start backend with: uvicorn app.main:app --reload")
        return 1

    results = [
        test_health(),
        test_providers(),
        test_analyze_no_keys(),
    ]

    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All checks passed! Backend is healthy.")
        print("\nNext steps:")
        print("1. Create backend/.env with your API keys (copy from backend/.env.example)")
        print("2. Restart backend: uvicorn app.main:app --reload")
        print("3. Test with real transcript: curl -X POST http://127.0.0.1:8000/api/analyze ...")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
