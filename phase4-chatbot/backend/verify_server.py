"""Simple script to verify chatbot backend is working.

Run this after starting the server with:
    uvicorn src.main:app --reload --port 8002
"""
import requests
import json

def test_endpoints():
    """Test all public endpoints."""
    base_url = "http://127.0.0.1:8002"

    print("=" * 60)
    print("CHATBOT BACKEND VERIFICATION")
    print("=" * 60)

    # Test 1: Health endpoint
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        if response.status_code == 200:
            print("   [OK] Health check passed")
        else:
            print("   [FAIL] Health check failed")
    except Exception as e:
        print(f"   [ERROR] {e}")

    # Test 2: Root endpoint
    print("\n2. Testing / endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        if response.status_code == 200:
            print("   [OK] Root endpoint passed")
        else:
            print("   [FAIL] Root endpoint failed")
    except Exception as e:
        print(f"   [ERROR] {e}")

    # Test 3: API docs
    print("\n3. Testing /docs endpoint...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] API docs accessible")
        else:
            print("   [FAIL] API docs not accessible")
    except Exception as e:
        print(f"   [ERROR] {e}")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print("\nIf all tests passed, the server is running correctly!")
    print("You can now test the chat endpoint with a valid JWT token.")

if __name__ == "__main__":
    test_endpoints()
