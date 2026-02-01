from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AnalysisResult:
    safety_score: int
    explanation: str
    consequence: str


class LLMProvider:
    name = "base"

    def analyze_item(self, path: str, metadata: Dict[str, str]) -> AnalysisResult:
        raise NotImplementedError

    def chat(self, messages: List[Dict[str, str]], context: Dict[str, str]) -> str:
        raise NotImplementedError
