import requests
import datetime

BASE_URL = "http://localhost:8001/api"
session = requests.Session()

def make_request(method, endpoint="/i-remember", headers=None, json_data=None):
    response = session.request(method, f"{BASE_URL}{endpoint}", headers=headers, json=json_data)
    print(f"{method} {response.status_code}: {response.json()}")
    return response

if __name__ == "__main__":
    # 1. Create location valid for 1 minute in Istanbul
    print("=== 1. Create Istanbul location (1 minute) ===")
    response = make_request("POST", json_data={
        "data": {"location": "Istanbul"},
        "valid": 1
    })
    key = response.json()["detail"]
    
    # 2. Get it
    print("\n=== 2. Get Istanbul location ===")
    make_request("GET", headers={"Authorization": key})
    
    # 3. Update to Ankara and make valid for 5 minutes
    print("\n=== 3. Update to Ankara (5 minutes) ===")
    make_request("PUT", headers={"Authorization": key}, json_data={
        "data": {"location": "Ankara"},
        "valid": 5
    })
    
    # 4. Get it
    print("\n=== 4. Get updated location ===")
    make_request("GET", headers={"Authorization": key})
    
    # 5. Delete it
    print("\n=== 5. Delete location ===")
    #make_request("DELETE", headers={"Authorization": key}, json_data={})
    
    session.close()