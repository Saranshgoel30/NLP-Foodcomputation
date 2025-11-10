import requests
import json

# Test the backend directly
url = "http://localhost:8000/search"
data = {
    "query": {
        "text": "paneer",
        "lang": "en",
        "constraints": None
    }
}

print("Testing backend at:", url)
print("Request data:", json.dumps(data, indent=2))

try:
    response = requests.post(url, json=data, timeout=10)
    print("\nStatus code:", response.status_code)
    print("Response:", response.text[:500])
except Exception as e:
    print("\nError:", str(e))
