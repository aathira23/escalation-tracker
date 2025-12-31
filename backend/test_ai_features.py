import requests
import json

BASE_URL = "http://localhost:8000"

def get_token():
    # Login as admin to get token
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={"username": "admin@example.com", "password": "adminpassword"}
    )
    if response.status_code == 200:
        return response.json()["accessToken"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_ai_insights(token):
    print("\n--- Testing AI Insights Endpoint ---")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics/insights", headers=headers)
    if response.status_code == 200:
        print("SUCCESS: Insights retrieved.")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"FAILED: {response.status_code} - {response.text}")

def test_clusters(token):
    print("\n--- Testing Complaint Clusters Endpoint ---")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics/clusters", headers=headers)
    if response.status_code == 200:
        clusters = response.json()
        print(f"SUCCESS: {len(clusters)} clusters retrieved.")
        for c in clusters:
            print(f"- {c['name']} ({c['count']} issues)")
    else:
        print(f"FAILED: {response.status_code} - {response.text}")

def test_recurrence_of_resolved(token):
    print("\n--- Testing Recurrence Detection (Resolved) ---")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get ACME Corp client ID
    clients_resp = requests.get(f"{BASE_URL}/api/clients", headers=headers)
    acme_id = None
    if clients_resp.status_code == 200:
        for client in clients_resp.json():
            if "ACME" in client["name"]:
                acme_id = client["id"]
                break
    
    if not acme_id:
        print("FAILED: Could not find ACME Corp client")
        return

    # Create first complaint
    title = "Login Failure - Production"
    complaint1 = {
        "title": title,
        "description": "Users cannot login to the production environment.",
        "client_id": acme_id,
        "priority": "critical"
    }
    
    resp1 = requests.post(f"{BASE_URL}/api/escalations", headers=headers, json=complaint1)
    if resp1.status_code == 200:
        e1_id = resp1.json()["id"]
        print(f"Original complaint created: {e1_id}")
        
        # Resolve it
        p_resp = requests.patch(f"{BASE_URL}/api/escalations/{e1_id}/status", headers=headers, json={"status": "resolved", "note": "Fixed by rebooting server"})
        if p_resp.status_code == 200:
            print(f"Original complaint resolved. New status: {p_resp.json()['status']}")
        else:
            print(f"Failed to resolve complaint: {p_resp.status_code} - {p_resp.text}")
            return
    else:
        print(f"Failed to create original complaint: {resp1.text}")
        return

    # Create second similar complaint
    complaint2 = {
        "title": "Login failure again",
        "description": "The login issue has returned.",
        "client_id": acme_id,
        "priority": "critical"
    }
    
    resp2 = requests.post(f"{BASE_URL}/api/escalations", headers=headers, json=complaint2)
    if resp2.status_code == 200:
        e2_id = resp2.json()["id"]
        print(f"Recurrent complaint created: {e2_id}")
        
        # Check notes for second complaint
        notes_resp = requests.get(f"{BASE_URL}/api/escalations/{e2_id}/notes", headers=headers)
        if notes_resp.status_code == 200:
            notes = notes_resp.json()
            found = False
            for note in notes:
                if "RECURRENCE DETECTED" in note["content"]:
                    print(f"SUCCESS: Resolved recurrence detected! Note: {note['content']}")
                    found = True
                    break
            if not found:
                print("FAILED: Resolved recurrence detection note not found.")
        else:
            print(f"Failed to fetch notes: {notes_resp.text}")
    else:
        print(f"Failed to create recurrent complaint: {resp2.text}")

def test_repeated_complaint(token):
    print("\n--- Testing Repeated Complaint Detection ---")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get ACME Corp client ID (common in our tests)
    clients_resp = requests.get(f"{BASE_URL}/api/clients", headers=headers)
    acme_id = None
    if clients_resp.status_code == 200:
        for client in clients_resp.json():
            if "ACME" in client["name"]:
                acme_id = client["id"]
                break
    
    if not acme_id:
        print("FAILED: Could not find ACME Corp client")
        return

    # Create first complaint
    complaint1 = {
        "title": "API Downtime - Urgent",
        "description": "Our API has been down for 2 hours.",
        "client_id": acme_id,
        "priority": "critical"
    }
    
    resp1 = requests.post(f"{BASE_URL}/api/escalations", headers=headers, json=complaint1)
    if resp1.status_code == 200:
        e1_id = resp1.json()["id"]
        print(f"First complaint created: {e1_id}")
    else:
        print(f"Failed to create first complaint: {resp1.text}")
        return

    # Create second similar complaint
    complaint2 = {
        "title": "API DOWN AGAIN - SOS",
        "description": "System still not responding.",
        "client_id": acme_id,
        "priority": "critical"
    }
    
    resp2 = requests.post(f"{BASE_URL}/api/escalations", headers=headers, json=complaint2)
    if resp2.status_code == 200:
        e2_id = resp2.json()["id"]
        print(f"Second complaint created: {e2_id}")
        
        # Check notes for second complaint
        notes_resp = requests.get(f"{BASE_URL}/api/escalations/{e2_id}/notes", headers=headers)
        if notes_resp.status_code == 200:
            notes = notes_resp.json()
            found = False
            for note in notes:
                if "Potential repeated complaint detected" in note["content"]:
                    print(f"SUCCESS: Repeated complaint detected! Note: {note['content']}")
                    found = True
                    break
            if not found:
                print("FAILED: Repeated complaint detection note not found.")
        else:
            print(f"Failed to fetch notes: {notes_resp.text}")
    else:
        print(f"Failed to create second complaint: {resp2.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        test_ai_insights(token)
        test_clusters(token)
        test_repeated_complaint(token)
        test_recurrence_of_resolved(token)
