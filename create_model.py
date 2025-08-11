import requests
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
base_url = config["server"]["base_url"]

model_name = "my_llama"  # Change as needed
modelfile_content = "FROM llama2\nPARAMETER temperature 0.7\n"

resp = requests.post(f"{base_url}/api/create", json={
    "name": model_name,
    "modelfile": modelfile_content
})
print(resp.json())