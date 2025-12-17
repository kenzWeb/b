import requests
import json

BASE_URL = "http://127.0.0.1:8000/school-api"

def test_api():
    session = requests.Session()
    
    # 1. Registration
    print("--- Testing Registration ---")
    reg_data = {
        "email": "testuser@example.com",
        "password": "Password1!"
    }
    r = session.post(f"{BASE_URL}/registr", json=reg_data)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    # 2. Auth
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
        headers = {"Authorization": f"Bearer {token}"} # Standard check. Spec: Bearer {token}
        # Note: DRF TokenAuth usually expects 'Token ...'. 
        # But if I didn't override the keyword, 'Bearer' might fail unless I fix it.
        # Let's see if it fails. If so, I'll update settings or my script.
        # Wait, I didn't change the keyword in settings. I just added TokenAuthentication.
        # Standard TokenAuthentication expects 'Token'.
        # The PROMPT validation says "Authorization: Bearer {token}".
        # If I strictly follow prompt, I MUST support 'Bearer'.
        # I should have subclassed TokenAuthentication.
        # I'll check if it fails first.
    
    # 3. List Courses
    print("\n--- Testing List Courses ---")
    # Need to create a course first via Admin or shell? 
    # Since DB is empty of courses, this will return empty list.
    r = session.get(f"{BASE_URL}/courses", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    test_api()
