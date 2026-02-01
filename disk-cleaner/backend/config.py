import json
import os
from dataclasses import dataclass, field
from typing import Dict, List

CONFIG_DIR = os.path.expanduser("~/.disk-cleaner")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_CONFIG = {
    "llm_provider": "ollama",
    "claude_api_key": "",
    "claude_model": "claude-3-5-sonnet-20241022",
    "ollama_base_url": "http://localhost:11434",
    "ollama_model": "llama3.1",
    "scan_locations": {},
}


@dataclass
class Settings:
    llm_provider: str
    claude_api_key: str
    claude_model: str
    ollama_base_url: str
    ollama_model: str
    scan_locations: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "Settings":
        os.makedirs(CONFIG_DIR, exist_ok=True)
        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "w", encoding="utf-8") as handle:
                json.dump(DEFAULT_CONFIG, handle, indent=2)
        with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        merged = {**DEFAULT_CONFIG, **data}
        return cls(
            llm_provider=merged["llm_provider"],
            claude_api_key=merged["claude_api_key"],
            claude_model=merged["claude_model"],
            ollama_base_url=merged["ollama_base_url"],
            ollama_model=merged["ollama_model"],
            scan_locations=merged.get("scan_locations", {}),
        )

    def save(self) -> None:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        data = {
            "llm_provider": self.llm_provider,
            "claude_api_key": self.claude_api_key,
            "claude_model": self.claude_model,
            "ollama_base_url": self.ollama_base_url,
            "ollama_model": self.ollama_model,
            "scan_locations": self.scan_locations,
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)


def history_log_path() -> str:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    return os.path.join(CONFIG_DIR, "history.log")
