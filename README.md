# AI-Document-Agent

AI-powered document intelligence agent that answers questions, generates summaries, and extracts key information using tool-based reasoning and LLMs.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. If you want to use a remote Ollama server on your LAN, configure `OLLAMA_BASE_URL`.

## Ollama Configuration

The project reads `OLLAMA_BASE_URL` from the environment first, then from a `.env` file in the project root.

- Default: `http://localhost:11434`
- Remote LAN example: `http://192.168.1.50:11434`

### Set via environment variable

Windows PowerShell:

```powershell
$env:OLLAMA_BASE_URL = "http://192.168.1.50:11434"
python main.py
```

macOS / Linux:

```bash
export OLLAMA_BASE_URL=http://192.168.1.50:11434
python main.py
```

### Set via `.env`

Create a `.env` file in the project root with:

```text
OLLAMA_BASE_URL=http://192.168.1.50:11434
```

## Run the agent

```bash
python main.py
```

You should see startup text and the configured Ollama base URL.

## Notes

- If the Ollama server is running locally, use the default URL.
- If Ollama runs on a different machine in the same LAN, use that machine's IP address.
- The code will use the configured base URL for all API calls.
