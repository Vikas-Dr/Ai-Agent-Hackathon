import requests
import json

try:
    response = requests.post("http://127.0.0.1:5050/api/report")
    print("Status:", response.status_code)
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Request failed:", e)
