"""Load local configuration and store OpenRouter credentials outside version control."""

import getpass
import os
from pathlib import Path
from typing import Dict


DEFAULT_MODEL = "openai/gpt-5.6-luna"


def load_project_env(path: str = ".env") -> Dict[str, str]:
    source = Path(path)
    loaded = {}
    if not source.exists():
        return loaded
    for raw_line in source.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name and name not in os.environ:
            os.environ[name] = value
            loaded[name] = value
    return loaded


def configure_openrouter(path: str = ".env", model: str = DEFAULT_MODEL) -> Path:
    destination = Path(path)
    key = getpass.getpass("Paste your OpenRouter API key (input is hidden): ").strip()
    if not key:
        raise ValueError("No API key was entered")
    destination.write_text(
        f"OPENROUTER_API_KEY={key}\nOPENROUTER_MODEL={model}\n",
        encoding="utf-8",
    )
    destination.chmod(0o600)
    return destination
