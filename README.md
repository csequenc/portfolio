# I Portfolio — Ishaan Maheshwari

A monochrome, desktop-inspired portfolio built with React, TypeScript, and Vite, with a separate FastAPI backend for the Ask Ishaan AI assistant.

## Project structure

- `src/` — React portfolio frontend.
- `backend/app/` — FastAPI service, portfolio knowledge base, and Groq-powered chat endpoint.
- `public/resume.pdf` — downloadable resume.

## Run locally

Requirements: Node.js 20.19+ (or 22.12+) and Python 3.10+.

### 1. Start the backend

From the project root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `backend/.env` and add your Groq API key:

```env
GROQ_API_KEY=your_real_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Then start the API:

```powershell
uvicorn app.main:app --reload --port 8000
```

The health endpoint is `http://localhost:8000/api/health` and interactive API docs are at `http://localhost:8000/docs`.

### 2. Start the frontend

Open a second terminal at the project root:

```powershell
npm install
npm run dev
```

Open the Vite URL (usually `http://localhost:5173`). Vite proxies `/api` requests to the local FastAPI server.

## Ask Ishaan architecture

1. The browser sends the latest question and a short session history to `POST /api/chat`.
2. FastAPI retrieves up to three relevant entries from `backend/app/knowledge.py`.
3. The backend sends only those curated portfolio notes to Groq, with instructions to stay grounded and not invent details.
4. The API returns the answer and the names of the notes used as sources.

The Groq API key stays in the backend environment and is never sent to the browser. Chat messages are not written to a database; the browser keeps the visible chat history in `sessionStorage` for the current tab session. The backend is stateless. The assistant can still miss a question if the lightweight keyword retriever cannot find the right notes; this can later be upgraded to embeddings without changing the frontend contract.

## Deployment

The included deployment setup is intended for **Vercel (frontend) + Render (FastAPI backend)**.

### Backend on Render

1. Push the project to GitHub.
2. Create a new Render Web Service from the repository and use `backend/render.yaml` (or configure the service manually with root directory `backend`, build command `pip install -r requirements.txt`, and start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
3. Add environment variables in Render:
   - `GROQ_API_KEY` — your Groq key.
   - `GROQ_MODEL` — `openai/gpt-oss-120b` (or another model available to your Groq account).
   - `FRONTEND_ORIGINS` — the exact deployed Vercel origin, e.g. `https://your-site.vercel.app`.
4. Confirm `https://YOUR-API.onrender.com/api/health` returns `{"status":"ok",...}`.

### Frontend on Vercel

1. Import the same GitHub repository into Vercel; the included `vercel.json` uses Vite's `dist` output.
2. Add the environment variable `VITE_API_BASE_URL` with the Render service origin, e.g. `https://YOUR-API.onrender.com` (no trailing slash).
3. Deploy. If you use a custom domain, add that exact origin to the backend's `FRONTEND_ORIGINS` value and redeploy/restart the backend.

The frontend build is static; the backend must be deployed separately for Ask Ishaan to answer. Keep `.env` files and API keys out of GitHub.

## Included applications

- **Welcome** — introduction and quick links.
- **Projects** — three selected projects, details, technologies, and repository links.
- **Resume** — embedded PDF viewer and download action.
- **JD Matcher** — local keyword-overlap comparison against terms in the resume. It is a heuristic, not an AI suitability score; the pasted JD is not uploaded.
- **Ask Ishaan** — Groq-powered assistant grounded in the curated portfolio knowledge base, with source labels and session-only chat history.
- **Contact** — email copy action and professional links.

## Desktop behaviour

- One application is visible at a time; Welcome opens by default.
- The sidebar switches applications. Closing the window returns to the empty desktop.
- Maximize/restore and close controls are provided; there is no minimize or dragging.
- On mobile, the sidebar becomes a bottom application dock and the app window uses the available screen space.
- `Escape` closes the current app. `Alt + →` cycles to the next app.

## Updating portfolio content

Project descriptions live in `src/content/projects.json`. Assistant facts and source text live in `backend/app/knowledge.py`. Update both when a project or resume detail changes.
