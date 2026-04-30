#!/usr/bin/env python3
"""
Quick setup guide for local development.
Run this to verify everything is working.
"""

import subprocess
import sys
import os
import json
import time

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def run_cmd(cmd, description):
    print(f"→ {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✓ Success")
            return True
        else:
            print(f"  ✗ Failed: {result.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    section("AI Interview Analyzer - Local Setup")
    
    # Check backend is running
    print("Checking if backend is running on http://127.0.0.1:8000...")
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2)
        print("✓ Backend is running!\n")
    except Exception as e:
        print(f"✗ Backend not running: {e}")
        print("\nStart backend with:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload --port 8000\n")
        return 1
    
    section("Test 1: Health Check")
    run_cmd(
        'curl -s http://127.0.0.1:8000/health',
        "Call /health endpoint"
    )
    
    section("Test 2: Provider Configuration")
    print("Checking which providers have API keys configured...\n")
    try:
        import urllib.request
        r = urllib.request.urlopen("http://127.0.0.1:8000/api/providers", timeout=5)
        data = json.loads(r.read().decode())
        print(f"  Preferred provider: {data.get('preferred_provider')}")
        print(f"  Gemini configured: {data.get('gemini_configured')}")
        print(f"  Groq configured: {data.get('groq_configured')}")
        print(f"  OpenAI configured: {data.get('openai_configured')}")
        print()
    except Exception as e:
        print(f"  Error: {e}\n")
    
    section("Test 3: Analyze Endpoint")
    print("Testing analyze endpoint (will fail without API keys - this is expected)...\n")
    run_cmd(
        'curl -s -X POST http://127.0.0.1:8000/api/analyze -H "Content-Type: application/json" -d "{\\"transcript\\": \\"Test\\"}"',
        "Call /api/analyze endpoint"
    )
    
    section("Setup Next Steps")
    
    env_example = "backend/.env.example"
    env_local = "backend/.env.local"
    
    if os.path.exists(env_local):
        print(f"✓ Found {env_local}")
    else:
        env_example = "backend/.env.example"
        if os.path.exists(env_example):
            print(f"✓ Found {env_example}")
    
    print(f"""
To make the backend fully functional:

1. Get a free API key from one of these services:
   
   🔵 Gemini (Recommended - most generous)
      → https://aistudio.google.com
      → Click "Get API Key" in left sidebar
   
   🟢 Groq (Fast inference on open-source models)
      → https://console.groq.com
      → Navigate to API Keys
   
   🟠 OpenAI (Chat GPT-based)
      → https://platform.openai.com/api-keys

2. Copy backend/.env.example to backend/.env:
   
   cp backend/.env.example backend/.env
   
   Or use backend/.env.local as a template

3. Edit backend/.env and paste your API key:
   
   GEMINI_API_KEY=your_key_here
   
   (or GROQ_API_KEY or OPENAI_API_KEY)

4. Restart the backend:
   
   # Kill running backend (Ctrl+C)
   # Then restart:
   
   python -m uvicorn app.main:app --reload --port 8000

5. Test with a real transcript:
   
   curl -X POST http://127.0.0.1:8000/api/analyze \\
     -H "Content-Type: application/json" \\
     -d '{{"transcript": "I have 5 years of experience as a senior backend engineer..."}}'

Then visit: http://127.0.0.1:5173 (frontend)
Or test via API: http://127.0.0.1:8000/health
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
