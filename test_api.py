#!/usr/bin/env python3
"""
Simple API Test Script - Test your LaughGraph APIs in real time!
Run this script to test your APIs quickly and easily.
"""

import requests
import json
import time
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_system_metrics():
    """Test the system metrics endpoint"""
    print("\n📊 Testing System Metrics...")
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_process_paper(arxiv_id: str = "2310.06825"):
    """Test processing a research paper"""
    print(f"\n📝 Testing Paper Processing for arXiv ID: {arxiv_id}...")
    
    # Step 1: Submit paper for processing
    try:
        payload = {
            "arxiv_id": arxiv_id,
            "user_query": "What are the main contributions of this paper?",
            "priority": "normal"
        }
        
        response = requests.post(f"{BASE_URL}/process-paper", json=payload)
        print(f"Submit Status Code: {response.status_code}")
        
        if response.status_code == 202:
            result = response.json()
            job_id = result["job_id"]
            print(f"Job ID: {job_id}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Step 2: Check job status
            print(f"\n⏳ Checking job status...")
            for i in range(10):  # Check up to 10 times
                status_response = requests.get(f"{BASE_URL}/job-status/{job_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Status Check {i+1}: {status_data['status']}")
                    
                    if status_data["status"] in ["completed", "failed"]:
                        print(f"Final Status: {json.dumps(status_data, indent=2)}")
                        break
                        
                time.sleep(2)  # Wait 2 seconds between checks
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_list_jobs():
    """Test listing all jobs"""
    print("\n📋 Testing List Jobs...")
    try:
        response = requests.get(f"{BASE_URL}/jobs")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 LaughGraph API Test Suite")
    print("=" * 50)
    
    # Test 1: Health Check
    if not test_health_check():
        print("❌ Health check failed - server might not be running")
        return
    
    # Test 2: System Metrics
    test_system_metrics()
    
    # Test 3: List Jobs (should be empty initially)
    test_list_jobs()
    
    # Test 4: Process a Paper
    print("\n" + "=" * 50)
    choice = input("🤔 Do you want to test paper processing? (y/n): ")
    if choice.lower() == 'y':
        arxiv_id = input("📄 Enter arXiv ID (press Enter for default '2310.06825'): ").strip()
        if not arxiv_id:
            arxiv_id = "2310.06825"
        test_process_paper(arxiv_id)
    
    # Test 5: List Jobs Again (should show our job)
    test_list_jobs()
    
    print("\n✅ Test suite completed!")
    print(f"🌐 API Documentation: {BASE_URL}/docs")
    print(f"📊 Live Metrics: {BASE_URL}/metrics")

if __name__ == "__main__":
    main()
