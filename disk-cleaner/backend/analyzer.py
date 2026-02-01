from dataclasses import asdict
from typing import Dict

from .config import Settings
from .llm.base import AnalysisResult, LLMProvider
from .llm.claude import ClaudeProvider
from .llm.ollama import OllamaProvider

DEFAULT_SCORES = {
    "safe": 90,
    "review": 65,
    "personal": 45,
}


class Analyzer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.provider = _build_provider(settings)

    def analyze(self, item: Dict[str, str]) -> Dict[str, str]:
        category = item.get("category", "review")
        fallback = AnalysisResult(
            safety_score=DEFAULT_SCORES.get(category, 50),
            explanation=item.get("default_explanation", ""),
            consequence=item.get("default_consequence", ""),
        )
        try:
            result = self.provider.analyze_item(item["path"], item)
        except Exception:
            result = fallback
        item.update(asdict(result))
        return item

    def chat(self, messages, context) -> str:
        try:
            return self.provider.chat(messages, context)
        except Exception as exc:
            return f"Unable to reach LLM provider: {exc}"


def _build_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "claude":
        return ClaudeProvider(settings.claude_api_key, settings.claude_model)
    return OllamaProvider(settings.ollama_base_url, settings.ollama_model)
