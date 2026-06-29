# AI-Document-Agent
AI-powered document intelligence agent that answers questions, generates summaries, and extracts key information using tool-based reasoning and LLMs.

## Ollama Configuration

The agent uses `OLLAMA_BASE_URL` to connect to the Ollama server.

- Default: `http://localhost:11434`
- To use a remote LAN server, set `OLLAMA_BASE_URL` to the remote address.

Example:

```bash
export OLLAMA_BASE_URL=http://192.168.1.50:11434
```

Or create a `.env` file in the project root containing:

```text
OLLAMA_BASE_URL=http://192.168.1.50:11434
```

This lets the same code work for both local and LAN-based Ollama servers.
