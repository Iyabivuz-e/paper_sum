#!/usr/bin/env python3
"""
🚀 Updated API Test - Now with SIMPLIFIED paper processing!
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"  # Update this if your server runs on different port

def test_simple_paper_processing():
    """Test the new SUPER SIMPLE paper processing endpoint"""
    print("🚀 Testing SIMPLIFIED Paper Processing")
    print("=" * 50)
    
    # Test Case 1: Just arXiv ID (minimal input!)
    print("📝 Test 1: Minimal input - just arXiv ID")
    simple_payload = {
        "arxiv_id": "2310.06825"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process-paper", json=simple_payload)
        print(f"✅ Request: POST /process-paper")
        print(f"✅ Payload: {json.dumps(simple_payload, indent=2)}")
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            job_id = result["job_id"]
            print(f"✅ Job ID: {job_id}")
            print(f"✅ Status: {result['status']}")
            return job_id
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_simple_with_query():
    """Test simple processing with custom query"""
    print("\n📝 Test 2: With custom user query")
    payload = {
        "arxiv_id": "2310.06825",
        "user_query": "What are the main technical innovations in this paper?"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process-paper", json=payload)
        print(f"✅ Request: POST /process-paper")
        print(f"✅ Payload: {json.dumps(payload, indent=2)}")
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job ID: {result['job_id']}")
            print(f"✅ Status: {result['status']}")
            return result["job_id"]
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_pdf_url():
    """Test with PDF URL instead of arXiv ID"""
    print("\n📝 Test 3: Using PDF URL instead of arXiv ID")
    payload = {
        "pdf_url": "https://arxiv.org/pdf/2310.06825.pdf"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process-paper", json=payload)
        print(f"✅ Request: POST /process-paper")
        print(f"✅ Payload: {json.dumps(payload, indent=2)}")
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job ID: {result['job_id']}")
            print(f"✅ Status: {result['status']}")
            return result["job_id"]
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def monitor_job(job_id):
    """Monitor a job's progress"""
    if not job_id:
        return
        
    print(f"\n⏳ Monitoring Job: {job_id}")
    print("-" * 30)
    
    for i in range(10):  # Check 10 times max
        try:
            response = requests.get(f"{BASE_URL}/job-status/{job_id}")
            if response.status_code == 200:
                data = response.json()
                status = data["status"]
                current_step = data.get("current_step", "unknown")
                
                print(f"Check #{i+1}: {status} - {current_step}")
                
                if status in ["completed", "failed"]:
                    print("\n🎉 Final Status:")
                    print(json.dumps(data, indent=2))
                    break
                    
            time.sleep(3)  # Wait 3 seconds
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            break

def show_examples():
    """Show example usage"""
    print("\n" + "=" * 60)
    print("📚 SIMPLIFIED API EXAMPLES")
    print("=" * 60)
    
    examples = [
        {
            "name": "Minimal - Just arXiv ID",
            "request": {"arxiv_id": "2310.06825"},
            "description": "Simplest possible request"
        },
        {
            "name": "With Custom Question",
            "request": {
                "arxiv_id": "2310.06825",
                "user_query": "What are the main contributions?"
            },
            "description": "Ask a specific question"
        },
        {
            "name": "Using PDF URL",
            "request": {"pdf_url": "https://arxiv.org/pdf/2310.06825.pdf"},
            "description": "Use direct PDF link instead"
        },
        {
            "name": "Both Sources",
            "request": {
                "arxiv_id": "2310.06825",
                "pdf_url": "https://arxiv.org/pdf/2310.06825.pdf",
                "user_query": "Explain the methodology"
            },
            "description": "Provide multiple sources and custom query"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print(f"   {example['description']}")
        print(f"   curl -X POST {BASE_URL}/process-paper \\")
        print(f"        -H 'Content-Type: application/json' \\")
        print(f"        -d '{json.dumps(example['request'])}'")

def main():
    print("🎉 SIMPLIFIED LAUGHGRAPH API TESTING!")
    print("Now you only need to provide arXiv ID or PDF URL - that's it!")
    
    # Show examples first
    show_examples()
    
    # Test the API
    print(f"\n🚀 Testing against: {BASE_URL}")
    
    # Test 1: Minimal input
    job1 = test_simple_paper_processing()
    
    # Test 2: With query
    job2 = test_simple_with_query()
    
    # Test 3: PDF URL
    job3 = test_pdf_url()
    
    # Monitor one job
    if job1:
        choice = input(f"\n🤔 Monitor job {job1}? (y/n): ")
        if choice.lower() == 'y':
            monitor_job(job1)
    
    print(f"\n✅ Testing Complete!")
    print(f"🌐 Interactive docs: {BASE_URL}/docs")
    print(f"📝 Try the simplified /process-paper endpoint!")

if __name__ == "__main__":
    main()
