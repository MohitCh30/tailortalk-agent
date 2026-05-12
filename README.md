# 📁 TailorTalk Drive Agent

A conversational AI agent that helps you search, filter, and discover files within a Google Drive folder using natural language. Built as part of the TailorTalk backend internship assignment.

**Live Demo:** [tailortalk-agent-67jpnwbsd6vczv6mx2qug5.streamlit.app](https://tailortalk-agent-67jpnwbsd6vczv6mx2qug5.streamlit.app)  
**Backend API:** [drive-agent.mohitchdev.me](https://drive-agent.mohitchdev.me/docs)

---

## What It Does

You type something like _"find all PDFs from April"_ or _"show me the employees spreadsheet"_ and the agent:

1. Translates your request into a Google Drive API `q` query string
2. Executes the search via the Drive API
3. Returns a clean, conversational response with file names, types, and modification dates

No RAG, no embeddings — just the Drive API doing what it's already good at, with an LLM as the query translator.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Agent Framework | LangChain tools + Groq LLM (manual pipeline, no agent loop) |
| LLM | Groq (`llama-3.1-8b-instant`) |
| Drive Integration | Google Drive API v3 via Service Account |
| Frontend | Streamlit |
| Backend Hosting | Cloudflare Tunnel → local FastAPI server |
| Frontend Hosting | Streamlit Cloud |
| Monitoring | Uptime Kuma |
| Process Management | systemd |

---

## Architecture

```
User (Streamlit UI)
        │
        ▼
FastAPI Backend (drive-agent.mohitchdev.me)
        │
        ├── LLM (Groq) translates natural language → Drive q param
        │
        ├── DriveSearchTool executes files.list(q=...) via Service Account
        │
        └── LLM formats results → conversational response
```

### How a query flows

1. User sends message: _"Find daily reports from April"_
2. LLM generates Drive query: `name contains 'daily' and modifiedTime > '2026-04-01T00:00:00'`
3. `DriveSearchTool` calls `files.list(q=full_query)` on the Drive API
4. Results returned with file name, type, and last modified date
5. LLM wraps results in a readable response

### Why not RAG?

The Drive API's `q` parameter supports searching by name, MIME type, full text content, and date ranges natively. Building a RAG pipeline on top would add complexity (chunking, embeddings, sync issues) without improving results. Knowing when not to use AI is part of good engineering.

---

## Deployment

### Backend — Cloudflare Tunnel

The FastAPI backend runs locally on port 8001 and is exposed publicly via a Cloudflare Tunnel — no open ports, no cloud provider needed.

```yaml
# ~/.cloudflared/config.yml
ingress:
  - hostname: drive-agent.mohitchdev.me
    service: http://localhost:8001
```

**Reliability features:**
- Monitored by [Uptime Kuma](https://github.com/louislam/uptime-kuma) via the `/health` endpoint
- Auto-restarts on laptop reboot via `systemd` service
- Cloudflare handles SSL termination and DDoS protection

### Frontend — Streamlit Cloud

Deployed directly from this GitHub repo. Streamlit Cloud pulls from `main` branch and serves `streamlit_app.py`.

---

## Running Locally

### Prerequisites

- Python 3.11+
- A Google Cloud project with Drive API enabled
- A Service Account with access to your target Drive folder
- A Groq API key

### Setup

```bash
git clone https://github.com/MohitCh30/tailortalk-agent
cd tailortalk-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
```

Place your `service_account.json` in the project root (never commit this).

### Google Drive Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project and enable the Google Drive API
3. Create a Service Account and download the JSON key as `service_account.json`
4. Share your target Drive folder with the service account email (Viewer access)
5. Copy the folder ID from the Drive URL into `.env`

### Run

Terminal 1 — Backend:
```bash
uvicorn main:app --reload --port 8001
```

Terminal 2 — Frontend:
```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501`

---

## Example Queries

| What you type | Drive query generated |
|---|---|
| Find all PDFs | `mimeType = 'application/pdf'` |
| Show me images | `mimeType contains 'image'` |
| Find files named report | `name contains 'report'` |
| Daily reports from April | `name contains 'daily' and modifiedTime > '2026-04-01T00:00:00'` |
| Find the employees file | `name contains 'employees'` |
| Search for invoice content | `fullText contains 'invoice'` |

---

## Project Structure

```
tailortalk-agent/
├── main.py           # FastAPI app, /chat and /health endpoints
├── agent.py          # LLM orchestration, chat history, query → response
├── drive_tool.py     # LangChain @tool wrapping Google Drive files.list
├── streamlit_app.py  # Chat UI
├── test_drive.py     # Quick Drive API connectivity test
├── requirements.txt
└── .gitignore
```

---

## Security Notes

- `service_account.json` and `.env` are gitignored and never committed
- Cloudflare Tunnel means no ports are exposed directly — all traffic goes through Cloudflare's network
- Service account has read-only (`drive.readonly`) scope
