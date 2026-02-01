import os
from typing import Dict, List

import requests

from .base import AnalysisResult, LLMProvider


class ClaudeProvider(LLMProvider):
    name = "claude"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def _request(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("Claude API key is not configured.")
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 512,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("content", [{"text": ""}])[0].get("text", "")

    def analyze_item(self, path: str, metadata: Dict[str, str]) -> AnalysisResult:
        prompt = (
            "You are a cautious disk cleanup assistant. "
            "Analyze the item and respond as JSON with keys "
            "safety_score (0-100), explanation, consequence.\n"
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
