import os
from pathlib import Path
from typing import Dict

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


def _load_dotenv(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                values[key] = value
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return values


def _normalize_base_url(url: str) -> str:
    candidate = url.strip()
    if not candidate:
        return DEFAULT_OLLAMA_BASE_URL
    if not candidate.startswith(("http://", "https://")):
        candidate = "http://" + candidate
    return candidate.rstrip("/")


def get_ollama_base_url() -> str:
    value = os.environ.get("OLLAMA_BASE_URL")
    if value:
        return _normalize_base_url(value)

    dotenv_values = _load_dotenv(Path.cwd() / ".env")
    if "OLLAMA_BASE_URL" in dotenv_values:
        return _normalize_base_url(dotenv_values["OLLAMA_BASE_URL"])

    return DEFAULT_OLLAMA_BASE_URL


OLLAMA_BASE_URL = get_ollama_base_url()
