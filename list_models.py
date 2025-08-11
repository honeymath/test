import requests
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
base_url = config["server"]["base_url"]

resp = requests.get(f"{base_url}/api/tags")
print(resp.json())