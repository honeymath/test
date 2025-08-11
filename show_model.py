import requests
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
base_url = config["server"]["base_url"]

model_name = "llama2"  # Change as needed
resp = requests.post(f"{base_url}/api/show", json={"name": model_name})
print(resp.json())