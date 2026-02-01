from typing import Dict, List

import requests

from .base import AnalysisResult, LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _request(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("response", "")

    def analyze_item(self, path: str, metadata: Dict[str, str]) -> AnalysisResult:
        prompt = (
            "You are a cautious disk cleanup assistant. "
            "Respond as JSON with keys safety_score (0-100), explanation, consequence.\n"
            f"Item: {path}\nMetadata: {metadata}"
        )
        raw = self._request(prompt)
        return _parse_analysis(raw)

    def chat(self, messages: List[Dict[str, str]], context: Dict[str, str]) -> str:
        prompt = (
            "You are a helpful disk cleanup copilot. "
            "Use the scan context to answer questions.\n"
            f"Context: {context}\nMessages: {messages}"
        )
        return self._request(prompt)


def _parse_analysis(raw: str) -> AnalysisResult:
    import json

    try:
        data = json.loads(raw)
        return AnalysisResult(
            safety_score=int(data.get("safety_score", 50)),
            explanation=str(data.get("explanation", "No explanation provided.")),
            consequence=str(data.get("consequence", "")),
        )
    except json.JSONDecodeError:
        return AnalysisResult(safety_score=50, explanation=raw.strip(), consequence="")
