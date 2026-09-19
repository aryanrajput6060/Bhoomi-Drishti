# Bhoomi-Drishti

**Bhoomi-Drishti** is a dual-purpose AI platform combining:

1. **BHUMI INSIGHT** — an AI-powered land-governance research and decision-intelligence platform (FastAPI + React/Vite SPA), built for Smart India Hackathon 2026 (PS26019).
2. **JARVIS** — a local desktop assistant framework with speech recognition (faster-whisper), LLM integration, TTS, skills, and system control.

Both systems coexist in one repository. The JARVIS backend lives under `jarvis/` and the BHUMI INSIGHT frontend/backend live under `frontend/` and `backend/`.

## Technology stack

| Layer | Technology |
|---|---|
| Backend (BHUMI INSIGHT) | Python 3.14, FastAPI, Uvicorn, Pydantic |
| Frontend (BHUMI INSIGHT) | React 19, TypeScript, Vite, Leaflet, Lucide React |
| JARVIS backend | Python 3.14, FastAPI, python-dotenv, httpx |
| STT (JARVIS) | faster-whisper (local Whisper models) |
| TTS (JARVIS) | Microsoft Edge TTS / Windows SAPI |
| Database | SQLite (via SQLAlchemy in JARVIS) |
| Deployment | Render (web service), cloudflared (tunnel, optional) |
## Project structure

```text
Bhoomi-Drishti/
├── .gitignore              # git ignore rules (includes jarvis/backend/data/)
├── .env.example            # environment variable template (NO real secrets)
├── .python-version         # Python 3.14.3
├── requirements.txt        # Python dependencies (BHUMI INSIGHT + JARVIS)
├── render.yaml             # Render Blueprint (FastAPI web service)
├── README.md               # this file
├── backend/               # BHUMI INSIGHT FastAPI backend
│   └── main.py            # FastAPI app, endpoints, mock data
├── frontend/             # BHUMI INSIGHT React/Vite SPA
│   ├── package.json
│   ├── vite.config.ts    # proxies /api -> http://127.0.0.1:8000
│   └── src/             # components, services, types, mock data
├── jarvis/              # JARVIS desktop assistant
│   └── backend/
│       ├── config.py    # central config (reads .env)
│       ├── services/    # stt, llm, tts, media, safety, scheduler ...
│       ├── skills/      # apps, assistant, media_control, shell ...
│       ├── brain/       # intent parsing / workflow engine
│       └── data/        # RUNTIME data — git-ignored, downloaded at runtime
## Installation

### Prerequisites

- **Python 3.14.3** (see `.python-version`; use `pyenv` or the Python launcher on Windows).
- **Node.js 20+** and **npm** for the frontend.
- **Windows** is the primary target for JARVIS (PowerShell scripts, sounddevice, SAPI TTS).

### Python backend

```bash
# From the repository root
python -m venv .venv
.venv\Scripts\activate            # on Windows

pip install -r requirements.txt
```

JARVIS also needs `python-dotenv` and `httpx` at runtime; those are listed in `requirements.txt`. For full JARVIS speech features, install:

```bash
pip install faster-whisper numpy sounddevice
```

The first time speech recognition is used, the Whisper model (`base.en` by default) is downloaded automatically into `jarvis/backend/data/whisper/`. That folder is **git-ignored** and should not be committed.

### Node frontend

```bash
cd frontend
npm install
```

## Environment variables

Copy `.env.example` to `.env` and fill in any values you need:

```bash
cp .env.example .env
```

Key variables (all optional unless noted):

| Variable | Purpose |
|---|---|
| `LLM_API_KEY` / `JARVIS_LLM_API_KEY` | OpenAI-compatible API key |
| `LLM_MODEL` | Override the default model name |
| `LLM_BASE_URL` | Override the API base URL |
| `TAVILY_API_KEY` | Tavily search |
| `SERPER_API_KEY` | Serper/Google search |
| `BRAVE_API_KEY` | Brave search |
| `HOME_ASSISTANT_URL` / `HOME_ASSISTANT_TOKEN` | Home automation |
| `WEBHOOK_URL` / `WEBHOOK_SECRET` | Outbound webhooks |
| `DEFAULT_CITY`, `WEATHER_LATITUDE`, `WEATHER_LONGITUDE` | Weather skill |

The JARVIS config (`jarvis/backend/config.py`) reads `jarvis/.env` by default. BHUMI INSIGHT currently uses hardcoded mock data and does not require API keys for the demo.

## How to run locally

### BHUMI INSIGHT (full stack)

```bash
# Terminal 1 - backend
.venv\Scripts\activate
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2 - frontend (from repo root)
cd frontend
npm run dev        # opens http://localhost:5173, proxies /api to backend
```

The frontend Vite config proxies `/api` requests to `http://127.0.0.1:8000`.

### JARVIS (desktop assistant)

JARVIS is a Python service framework. Run the JARVIS backend directly:

```bash
.venv\Scripts\activate
cd jarvis/backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The Whisper model is downloaded on first use; ensure `jarvis/backend/data/` is writable and not git-tracked.

## Whisper / model setup

- JARVIS uses **faster-whisper** for local speech recognition.
- The default model is `base.en` (configured in `jarvis/backend/config.py`).
- On first transcription, the model is downloaded to:

  ```
  jarvis/backend/data/whisper/models--Systran--faster-whisper-base.en/
  ```

- That folder is **git-ignored** (`.gitignore` includes `jarvis/backend/data/`).
- The `.gitignore` also ignores `**/models/`, `**/model_cache/`, `**/huggingface/`, and `**/.cache/`.

**Deployment note:** On a new machine, the Whisper model will be downloaded automatically the first time speech recognition runs, provided `faster-whisper` is installed and the machine has internet access. No pre-committed model binary is required.

## Deployment notes

- The `render.yaml` blueprint deploys a single FastAPI web service (`backend/`) that also serves the built React SPA from `frontend/dist/`.
- The build command installs Python deps, then builds the frontend with `npm ci && npm run build`.
- The start command runs `uvicorn main:app --host 0.0.0.0 --port $PORT` from `backend/`.
- Set `PYTHON_VERSION=3.14.3` (or match `.python-version`) in the Render environment.
- The frontend build output (`frontend/dist/`) is git-ignored and regenerated during deployment.

## Important files that are intentionally ignored

| Path | Reason |
|---|---|
| `jarvis/backend/data/` | Runtime data: SQLite DB, screenshots, TTS cache, Whisper model |
| `.env` / `.env.*` | Secrets and local config (use `.env.example` as a template) |
| `node_modules/` | Installed npm packages |
| `frontend/dist/` | Built frontend (regenerated by `npm run build`) |
| `.venv/` / `venv/` / `env/` | Python virtual environments |
| `__pycache__/`, `*.pyc`, `*.pyo` | Python bytecode |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | Tool caches |
| `cloudflared.exe` | Cloudflare tunnel binary |
| `dist/`, `build/`, `.next/`, `out/` | Generic build output |
| `*.log` | Log files |

## GitHub readiness

- Large generated/model files are excluded via `.gitignore` and (if previously committed) via Git history rewriting.
- Secrets are kept out of the repository via `.gitignore` and `.env.example`.
- Generated caches, build artifacts, and virtual environments are excluded.
- After preparing the repository locally, run `git status` to confirm only intended files are staged before pushing.

## License

This project is developed as part of Smart India Hackathon 2026 (PS26019). See the repository for any applicable license terms.
└── tests/              # BHUMI INSIGHT tests (test_jarvis_brain.py)
```
| Python version | 3.14.3 (see `.python-version`) |
