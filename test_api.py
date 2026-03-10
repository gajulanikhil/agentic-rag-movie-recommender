import requests
import json

url = "http://localhost:8000/api/chat"
payload = {
    "prompt": "Recommend a highly rated sci-fi movie",
    "min_year": 1950,
    "max_year": 2024,
    "min_rating": 0,
    "content_type": "All"
}

try:
    print("Sending request...")
    response = requests.post(url, json=payload, timeout=120)
    data = response.json()
    print("Response JSON:")
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
