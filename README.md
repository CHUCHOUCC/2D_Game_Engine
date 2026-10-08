# 2D Engine · Backend (Python)

FastAPI API: login, projects (game scenes) and a call to the separate AI service. The data structures are written by hand (no `list.append/pop`, `deque` or `queue.Queue`).

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
| `POST /auth/register` | Create an account (username, email, password of 8+ characters) |
| `POST /auth/login` | Check the password and return a bearer token |
| `GET /auth/me` | The logged-in user |
| `POST /auth/logout` | Invalidate the token |
| `POST /projects` | Create a project (empty scene) |
| `GET /projects` | List the owner's projects |
| `GET /projects/{id}` | Load one project |
| `PUT /projects/{id}/scene` | Save the scene (list of game objects) |
| `POST /projects/{id}/ai` | Ask the separate AI service for objects and add them to the scene |

All `/projects` routes need the header `Authorization: Bearer <token>`.
Every project query filters by `owner_id` (the id of the logged-in user), so one user cannot read or change another user's project: they get 404.

## Login module (`app/auth/`)

| Class | Responsibility |
|---|---|
| `PasswordHasher` | Salted scrypt: `create` makes (salt, hash), `verify` re-hashes and compares in constant time |
| `TokenGenerator` | Makes a random token (`secrets.token_urlsafe`) and hashes it with SHA-256 |
| `User` | Id, username, email, salt and hash; read-only properties; `repr` hides the secrets |
| `Session` | Token hash, owner and expiry date; `is_valid()` |
| `UserRepository`, `SessionRepository` | Hand-written SQL for the `users` and `sessions` tables |
| `AuthService` | `register`, `log_in`, `user_from_token`, `log_out`; the rules live here |
| `router.py`, `dependencies.py` | HTTP routes and the `current_user` dependency (reads the bearer token) |

- Passwords are never stored: only a random 16-byte salt and the scrypt hash.
- The token is returned once; the database only keeps its SHA-256 hash, so a leaked database does not leak sessions.
- Tokens expire (`SESSION_DURATION` in `auth_service.py`) and stop working after logout.
- Wrong password and unknown email give the same answer, so the API does not reveal which emails exist.

## Tests

```powershell
python -m pytest
```

The SQL repositories also have integration tests that need a throw-away PostgreSQL database with the project's tables.
They are skipped unless `TEST_DATABASE_URL` is set (never point it at the production database).

## Deployment (Render or similar)

- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Dependencies: `requirements.txt`
- Environment variables: `DATABASE_URL`, `FRONTEND_ORIGINS` (allowed browser origins, comma separated), `AI_SERVICE_URL` and `AI_SERVICE_KEY` (the separate AI service and the secret it shares with this backend)
- Secrets (`API_KEY`, `DATABASE_URL`) go in the service's environment variables, never in the code.
