#!/usr/bin/env python3

import requests
import json

# Test the API
def test_api():
    base_url = "http://localhost:3009"
    
    print("🧪 Testing Plagiarism Detection API...")
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Analyze plagiarism
    print("\n2️⃣ Testing plagiarism analysis...")
    payload = {
        "repo_url": "https://github.com/Michael069m/Stock-Price-Predictor-project",
        "language": "Python",
        "min_stars": 5,
        "max_candidates": 3
    }
    
    try:
        print(f"📤 Sending request to: {base_url}/analyze-plagiarism")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{base_url}/analyze-plagiarism",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"🎯 Suspect Repo: {result['suspect_repo']['name']}")
            print(f"📊 Topic: {result['suspect_repo']['topic']}")
            print(f"🔍 Keywords: {', '.join(result['suspect_repo']['keywords'][:5])}...")
            print(f"⚠️  Plagiarism Detected: {result['plagiarism_detected']}")
            print(f"📈 Candidates Checked: {result['summary']['total_candidates_checked']}")
        else:
            print("❌ Error:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api()
