#!/usr/bin/env python3
"""
Simple test script for the cleaned-up paper processing API
"""

import requests
import time
import json
import sys

API_BASE = "http://localhost:8001"  # Adjust port as needed

def test_simple_api():
    """Test the simplified paper processing API"""
    print("🧪 Testing Simple Paper Processing API")
    print("=" * 50)
    
    # Test 1: Health check
    print("1️⃣ Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Simple paper processing
    print("\n2️⃣ Testing simple paper processing...")
    try:
        # Process the famous "Attention Is All You Need" paper
        payload = {
            "arxiv_id": "1706.03762"
        }
        
        print(f"   Submitting job with payload: {payload}")
        response = requests.post(f"{API_BASE}/process-paper", json=payload)
        
        if response.status_code != 200:
            print(f"❌ Job submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        job_data = response.json()
        job_id = job_data["job_id"]
        print(f"✅ Job submitted successfully")
        print(f"   Job ID: {job_id}")
        print(f"   Status: {job_data['status']}")
        
        # Test 3: Check job status
        print("\n3️⃣ Monitoring job progress...")
        max_attempts = 30  # 5 minutes max
        for attempt in range(max_attempts):
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data["status"]
                    print(f"   Attempt {attempt + 1}: Status = {current_status}")
                    
                    if current_status == "completed":
                        print("✅ Job completed successfully!")
                        
                        # Test 4: Get results in different formats
                        print("\n4️⃣ Testing result formats...")
                        
                        # Test JSON format
                        json_response = requests.get(f"{API_BASE}/jobs/{job_id}/download/json")
                        if json_response.status_code == 200:
                            print("✅ JSON format available")
                            results = json.loads(json_response.text)
                            print(f"   Title: {results.get('paper_metadata', {}).get('title', 'N/A')}")
                            print(f"   Novelty Score: {results.get('novelty_score', 'N/A')}")
                        
                        # Test Markdown format
                        md_response = requests.get(f"{API_BASE}/jobs/{job_id}/download/markdown")
                        if md_response.status_code == 200:
                            print("✅ Markdown format available")
                            print(f"   Length: {len(md_response.text)} characters")
                        
                        return True
                        
                    elif current_status == "failed":
                        print(f"❌ Job failed")
                        if "error_message" in status_data:
                            print(f"   Error: {status_data['error_message']}")
                        return False
                    
                    # Still processing, wait and retry
                    time.sleep(10)
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"⚠️ Status check error: {e}")
                time.sleep(10)
        
        print(f"⏰ Job timed out after {max_attempts} attempts")
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API Tests")
    print(f"📡 API Base URL: {API_BASE}")
    print()
    
    success = test_simple_api()
    
    if success:
        print("\n🎉 All tests passed! The API is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed! Check the server and try again.")
        sys.exit(1)
