# 2D Engine · Backend (Python)

FastAPI API. For now it only has `GET /health` and the hand-written data structures (no `list.append/pop`, `deque` or `queue.Queue`).

## Run locally (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest            # tests
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/health, which must answer `{"ok": true}`. The automatic docs are at `/docs`.

## Structures and plan exercises

| Code | Exercise | What it shows |
|---|---|---|
| `app/structures/stack.py` | 3, position stack | LIFO, top, undo; O(1) |
| `app/structures/queue.py` | 4, event queue | FIFO with front and rear; O(1) |
| `app/structures/tree.py` | 5, expression tree | postorder traversal; O(n) |
| `app/domain/score_counter.py` | 1, score counter | rule for each event |

Each file documents its invariant, its costs and what happens when the structure is empty.

## Database and API

PostgreSQL on Supabase, accessed with `psycopg` and hand-written SQL in repository classes.
Copy `.env.example` to `.env` and set `DATABASE_URL` (never commit `.env`).

| Route | What it does |
|---|---|
| `GET /health` | Liveness check |
| `POST /projects` | Create a project (empty scene) |
| `GET /projects` | List the owner's projects |
| `GET /projects/{id}` | Load one project |
| `PUT /projects/{id}/scene` | Save the scene (list of game objects) |
| `POST /projects/{id}/ai` | Ask the separate AI service for objects and add them to the scene |

Every project query filters by `owner_id`, so one user cannot read or change another user's project.
Until the login module is finished, the owner is a fixed demo user (id 1).

## Deployment (Render or similar)

- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Dependencies: `requirements.txt`
- Environment variables: `DATABASE_URL`, `FRONTEND_ORIGINS` (allowed browser origins, comma separated), `AI_SERVICE_URL` and `AI_SERVICE_KEY` (the separate AI service and the secret it shares with this backend)
- Secrets (`API_KEY`, `DATABASE_URL`) go in the service's environment variables, never in the code.
