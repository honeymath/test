# test

Test GPT API and Ollama API utilities.

## Configuring `config.ini`
This project uses a `config.ini` file to store the Ollama API server address. This file is **ignored by Git** for security and flexibility.

### Example `config.ini`
```ini
[server]
base_url = http://localhost:11434
```

- `base_url` — The base URL of your Ollama API server.
- Change it to match your server location or port.

Once configured, you can run the Python scripts in this folder to interact with Ollama, such as listing models, pulling models, chatting, generating text, etc.
