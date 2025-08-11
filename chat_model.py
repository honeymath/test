import requests
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
base_url = config["server"]["base_url"]

model_name = "llama2"  # Change as needed
messages = [
    {"role": "user", "content": "Hello, how are you?"}
]

resp = requests.post(f"{base_url}/api/chat", json={
    "model": model_name,
    "messages": messages
})
print(resp.json())