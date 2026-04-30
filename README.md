# AI Interview Analyzer

This repository contains a deployable full-stack app for analyzing interview transcripts.

- FastAPI backend at `backend/`
- React + Vite frontend at `frontend/`
- Strict JSON prompt for topics, profile, and summary
- Provider support for Gemini, Groq, and OpenAI

## Project Structure

- `backend/` - FastAPI service, prompt logic, and LLM provider adapters
- `backend/api/index.py` - Vercel serverless entrypoint for FastAPI app
- `backend/vercel.json` - backend Vercel routing/build config
- `frontend/` - Vite app with transcript upload, loading states, and polished output UI
- `frontend/vercel.json` - frontend SPA rewrite config for Vercel
- `summarizer.py` - standalone CLI from the earlier prompt iteration work
- `prompt_iterations.md` - prompt iteration log

## Setup

Create provider keys in the appropriate `.env` files:

`backend/.env`

Create `backend/.env` from `backend/.env.example`. Do NOT commit your real `.env` file — it was accidentally committed earlier and has been removed from the repository. The repo includes `backend/.env.example` as a template.

Example (copy into `backend/.env` and fill keys):

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
ALLOWED_ORIGINS=http://localhost:5173
```

`frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_LLM_PROVIDER=gemini
```

## Run Locally

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and submit a transcript.

## Deploy on Vercel (Single Monolithic Deployment)

Use one Vercel project from repo root. The root [vercel.json](e:/projects/Automated%20Interview%20Analysis%20using%20LLMs/vercel.json) builds both parts:

- Python serverless function from `backend/api/index.py`
- Static frontend build from `frontend/package.json`

### Steps

1. In Vercel, create one project and set Root Directory to the repository root.
2. Keep framework auto-detection/defaults. Root `vercel.json` controls build and routing.
3. Add backend environment variables in Vercel Project Settings:
   - `LLM_PROVIDER`
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL`
   - `GROQ_API_KEY`
   - `GROQ_MODEL`
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL`
   - `ALLOWED_ORIGINS` (set to your Vercel app URL)
4. Optional frontend env var:
   - `VITE_API_BASE_URL` (leave unset for same-origin `/api` routing in monolithic mode)
5. Deploy.

After deploy:

- App UI: `https://<your-app-domain>/`
- Health check: `https://<your-app-domain>/health`
- Analyze API: `https://<your-app-domain>/api/analyze`

## API Usage

POST `/api/analyze` (local: `http://localhost:8000/api/analyze`, deployed: backend domain + `/api/analyze`)

Request body:

```json
{
  "transcript": "...",
  "provider": "gemini",
  "model": "gemini-2.0-flash"
}
```

Response body:

```json
{
  "topics_covered": [],
  "profile": {
    "role": "",
    "level": "",
    "justification": ""
  },
  "candidate_summary": ""
}
```

## LLM Used

The app is provider-agnostic. The recommended default is Gemini `gemini-2.0-flash`, with Groq `llama-3.1-8b-instant` and OpenAI `gpt-4o-mini` supported as alternatives.

## Reflection

The biggest surprise was how much more reliable the output became once the prompt forced concrete topics, a dominant role decision, and an explicit fallback for missing evidence. The backend is intentionally simple and modular so it can be swapped to another model provider without touching the UI. A deterministic provider fallback and transient-retry logic have been implemented so the service will attempt Gemini → Groq → OpenAI (configurable via `LLM_PROVIDER`) and retry transient errors automatically.

The main limitation is that transcript quality still controls the ceiling of the result: vague interviews produce weaker profiles and more `Not enough evidence` fields. Another practical limitation is that the app requires valid LLM API keys set in the backend environment before it can analyze anything; see `backend/.env.example` for the expected variables.

Security note — exposed keys found and removed
---------------------------------------------
- During development an actual `.env` with API keys was accidentally created and has been removed from the repository.
- If you used any real API keys while developing, PLEASE ROTATE/REVOKE those keys now — they may have been exposed.
- To remove secrets from Git history, use a tool such as `git filter-repo` or the BFG Repo-Cleaner. Example (run locally):

```bash
# Install git-filter-repo (if not installed) and run to remove a path from history
pip install git-filter-repo
git filter-repo --path backend/.env --invert-paths
```

After scrubbing history, force-push the cleaned branch to your remote and rotate any keys that were committed.

"# Interview-Transcript-Analyzer-with-Structured-Insights" 
