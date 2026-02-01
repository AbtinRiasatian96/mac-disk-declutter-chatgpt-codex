# Disk Cleaner (Local Mac Cleanup)

A local-first Mac cleanup assistant that scans common locations, ranks items by ROI (space freed × safety), and provides a chat co-pilot for questions. The backend is a Python Flask server that serves a lightweight web UI.

## Features
- Scan predefined macOS locations, including caches, logs, simulators, backups, downloads, and trash.
- LLM-backed analysis with switchable Claude or Ollama providers.
- ROI-based ranking and aggregated items.
- Checkbox selection with delete options (move to Trash or permanent delete).
- Context-aware chat co-pilot.
- Logs deletions to `~/.disk-cleaner/history.log`.

## Project Structure
```
disk-cleaner/
├── backend/
│   ├── app.py
│   ├── scanner.py
│   ├── analyzer.py
│   ├── llm/
│   │   ├── base.py
│   │   ├── claude.py
│   │   └── ollama.py
│   ├── cleaner.py
│   └── config.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt
└── README.md
```

## Setup
```bash
cd disk-cleaner
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
cd disk-cleaner
export OPEN_BROWSER=1
python -m backend.app
```

The app starts on `http://localhost:5000` and optionally opens a browser.

## Configuration
Settings are stored in `~/.disk-cleaner/config.json`:
- `llm_provider`: `ollama` or `claude`
- `claude_api_key`: API key for Claude
- `claude_model`: Claude model name
- `ollama_base_url`: Base URL for Ollama (default `http://localhost:11434`)
- `ollama_model`: Model name for Ollama

You can edit this file directly or use the `/api/settings` endpoint.

## Safety Notes
- Nothing is deleted automatically.
- Permanent deletes require confirmation.
- All deletions are logged.

## API Endpoints
- `POST /api/scan`: Scan locations and return ranked results.
- `POST /api/delete`: Delete selected items (trash or permanent).
- `POST /api/chat`: Chat with the co-pilot.
- `GET/POST /api/settings`: Read or update settings.
