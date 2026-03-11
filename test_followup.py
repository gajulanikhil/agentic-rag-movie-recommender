import requests
import json
import time

url = "http://localhost:8000/api/chat"

# Turn 1: Broad recommendation
payload1 = {
    "prompt": "Recommend me an action movie.",
    "session_id": "test_session_123",
    "min_year": 1950,
    "max_year": 2024,
    "min_rating": 0.0,
    "content_type": "All"
}

print("SENDING: Turn 1 (Recommendation)")
res1 = requests.post(url, json=payload1, timeout=120)
print(json.dumps(res1.json(), indent=2))
print("\n" + "="*50 + "\n")

time.sleep(2)

# Turn 2: Specific follow-up
payload2 = {
    "prompt": "Tell me more about Mad Max movie",
    "session_id": "test_session_123",
    "min_year": 1950,
    "max_year": 2024,
    "min_rating": 0.0,
    "content_type": "All"
}

print("SENDING: Turn 2 (Specific Detail)")
res2 = requests.post(url, json=payload2, timeout=120)
print(json.dumps(res2.json(), indent=2))
