import requests
import json

BASE_URL = "http://127.0.0.1:8000/school-api"

def test_api():
    session = requests.Session()
    
    
    print("--- Testing Registration ---")
    reg_data = {
        "email": "testuser@example.com",
        "password": "Password1!"
    }
    r = session.post(f"{BASE_URL}/registr", json=reg_data)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    
    print("\n--- Testing Auth ---")
    auth_data = {
        "email": "testuser@example.com",
        "password": "Password1!"
    }
    r = session.post(f"{BASE_URL}/auth", json=auth_data)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    if r.status_code == 200:
        token = r.json().get('token')
        headers = {"Authorization": f"Bearer {token}"} 
        
        
        
        
        
        
        
        
        
    
    
    print("\n--- Testing List Courses ---")
    
    
    r = session.get(f"{BASE_URL}/courses", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    test_api()
