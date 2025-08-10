import requests
import json

url = "https://natural-whole-liger.ngrok-free.app/api/generate"
headers = {
    "Content-Type": "application/json"
}
payload = {
    "model": "gpt-oss:20b",
    "prompt": "This is a test, please tell a very short story in one sentence.",
    "stream": False,
    "max_tokens": 10
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    print(response.text)
except requests.RequestException as e:
    print(f"Request failed: {e}")
