import json
import os
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .analyzer import Analyzer
from .cleaner import delete_items
from .config import Settings
from .scanner import scan

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/scan", methods=["POST"])
def scan_endpoint():
    settings = Settings.load()
    analyzer = Analyzer(settings)
    items = [analyzer.analyze(item) for item in scan(settings)]
    ranked = sorted(items, key=_roi_score, reverse=True)
    return jsonify({"items": ranked, "provider": settings.llm_provider})


@app.route("/api/delete", methods=["POST"])
def delete_endpoint():
    payload = request.get_json(force=True)
    mode = payload.get("mode", "trash")
    if mode not in {"trash", "permanent"}:
        return jsonify({"error": "Invalid mode."}), 400
    paths = payload.get("paths", [])
    delete_items(paths, mode)
    return jsonify({"status": "ok", "deleted": len(paths)})


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    payload = request.get_json(force=True)
    messages = payload.get("messages", [])
    context = payload.get("context", {})
    settings = Settings.load()
    analyzer = Analyzer(settings)
    response = analyzer.chat(messages, context)
    return jsonify({"response": response})


@app.route("/api/settings", methods=["GET", "POST"])
def settings_endpoint():
    settings = Settings.load()
    if request.method == "POST":
        payload = request.get_json(force=True)
        settings.llm_provider = payload.get("llm_provider", settings.llm_provider)
        settings.claude_api_key = payload.get("claude_api_key", settings.claude_api_key)
        settings.claude_model = payload.get("claude_model", settings.claude_model)
        settings.ollama_base_url = payload.get("ollama_base_url", settings.ollama_base_url)
        settings.ollama_model = payload.get("ollama_model", settings.ollama_model)
        settings.save()
    return jsonify(
        {
            "llm_provider": settings.llm_provider,
            "claude_api_key": bool(settings.claude_api_key),
            "claude_model": settings.claude_model,
            "ollama_base_url": settings.ollama_base_url,
            "ollama_model": settings.ollama_model,
        }
    )


def _roi_score(item):
    return item.get("size_bytes", 0) * item.get("safety_score", 0)


def open_browser(port: int = 5000) -> None:
    webbrowser.open(f"http://localhost:{port}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    if os.environ.get("OPEN_BROWSER", "1") == "1":
        open_browser(port)
    app.run(host="0.0.0.0", port=port, debug=True)
