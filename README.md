# 2D Engine · Backend (Python)

FastAPI API of the 2D game engine: JWT login, projects (game scenes), game runs, the AI that
learns from those runs, and the settings of the editor. The data structures in `app/structures/`
are written by hand (no `list.append/pop`, `deque` or `queue.Queue`).

```
Frontend ──► Backend (this repo) ──► PostgreSQL (53 tables)
                  │
                  └── service token (JWT, 60 s) ──► AI service ──► optional external AI API
```

## Run locally (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env        # set DATABASE_URL, JWT_SECRET, AI_SERVICE_URL, AI_SERVICE_KEY
python -m app.migrate         # creates or updates the tables
python -m pytest              # tests
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/health (`{"ok": true}`) and http://127.0.0.1:8000/health/db
(number of migrations applied). The automatic docs are at `/docs`.

## Structures and plan exercises

| Code | Exercise | What it shows |
|---|---|---|
| `app/structures/stack.py` | 3, position stack | LIFO, top, undo; O(1) |
| `app/structures/queue.py` | 4, event queue | FIFO with front and rear; O(1) |
| `app/structures/tree.py` | 5, expression tree | postorder traversal; O(n) |
| `app/domain/score_counter.py` | 1, score counter | rule for each event |

Each file documents its invariant, its costs and what happens when the structure is empty.

## Database

53 tables, created by the numbered SQL files in `migrations/`. See [docs/database.md](docs/database.md)
for every table and for running the SQL tests on a throw-away PostgreSQL.

## Tokens

JWT access tokens (15 min), rotating refresh tokens (7 days, reuse detection) and signed service
tokens between the backend and the AI service. See [docs/tokens.md](docs/tokens.md).

## API

All routes except `/health`, `/auth/register`, `/auth/login` and `/auth/refresh` need
`Authorization: Bearer <access_token>`. Every project query filters by the logged-in user, so
another user's project answers 404.

| Route | What it does |
|---|---|
| `POST /auth/register` | Create an account (username, email, password of 8+ characters) |
| `POST /auth/login` | Access + refresh token; 429 after 5 failures in 15 minutes |
| `POST /auth/refresh` | Rotate the refresh token and get a new pair |
| `GET /auth/me` | The logged-in user |
| `POST /auth/logout`, `POST /auth/logout-all` | Revoke this login or every login |
| `GET/PUT /me/settings` | Theme, language, grid, volumes (settings wheel) |
| `GET/PUT /me/profile`, `GET /me/activity` | Profile and recent security events |
| `GET /me/stats`, `GET /me/achievements` | Player totals and unlocked achievements |
| `GET /projects/templates` | Starter scenes |
| `POST /projects`, `GET /projects` | Create (optionally from a template) and list |
| `GET/PATCH/DELETE /projects/{id}` | Load, rename, delete |
| `POST /projects/{id}/duplicate` | Clone a project |
| `PUT /projects/{id}/scene` | Save the scene; every save stores a version |
| `GET /projects/{id}/versions`, `POST .../versions/{n}/restore` | History and restore |
| `POST /projects/{id}/ai` | Objects from a text prompt |
| `POST /projects/{id}/ai/obstacles` | Obstacles placed by the learned model |
| `GET /projects/{id}/ai/model` | What the AI has learned for this level |
| `POST /projects/{id}/plays`, `POST .../plays/{run}/finish` | Start and finish a run; the AI learns from it |
| `GET /projects/{id}/leaderboard` | Best scores of the level |
| `GET /catalog/kinds`, `/catalog/enemies`, `/catalog/textures` | Object kinds with physics, enemies, texture pack |

Object kinds: `player` (one per scene), `box`, `wall`, `house`, `tree`, `spike`, `coin`, `enemy`.
The world is 1600 × 960 pixels; objects outside it are rejected, also when they come from the AI.

## How the AI learns

1. `POST /plays` starts a run with the level's current difficulty.
2. When the run ends, the game sends its numbers to `POST /plays/{run}/finish`.
3. The backend saves the run, updates the player's totals, high scores and achievements, then
   sends the run and the level's model to the AI service (`/learn`).
4. The AI service returns the updated model and the reward; the backend stores both
   (`ai_models`, `ai_training_samples`).
5. `POST /ai/obstacles` asks the AI to place new obstacles with that model: levels that are won
   easily get more and harder obstacles, levels where players keep dying get fewer.

If the AI service is down, the run is still saved (`"learned": false`).

## Login module (`app/auth/`)

| Class | Responsibility |
|---|---|
| `PasswordHasher` | Salted scrypt: `create` makes (salt, hash), `verify` compares in constant time |
| `TokenGenerator` | Random refresh tokens and their SHA-256 hash |
| `JwtCodec` | Signs and checks access tokens |
| `ServiceTokenIssuer` | Signs the 60-second tokens sent to the AI service |
| `AuthService` | `register`, `log_in`, `refresh`, `user_from_token`, `log_out`, `log_out_everywhere` |
| `UserRepository`, `RefreshTokenRepository`, `RevokedTokenRepository`, `LoginAttemptRepository` | Hand-written SQL |
| `router.py`, `dependencies.py` | HTTP routes and the `current_user` dependency |

- Passwords are never stored: only a random 16-byte salt and the scrypt hash.
- Unknown email and wrong password take the same time and give the same answer.
- Every response carries security headers (`nosniff`, `DENY`, no referrer, strict CSP).

## Tests

```powershell
python -m pytest
```

The SQL repositories have integration tests that need a throw-away PostgreSQL with the
migrations applied. They are skipped unless `TEST_DATABASE_URL` is set (never production).
CI (`.github/workflows/tests.yml`) runs everything against PostgreSQL 16.

## Deployment (Render or similar)

- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Before the first start and after every update: `python -m app.migrate`
- Once a day (optional): `python -m app.maintenance`
- Environment variables: `DATABASE_URL`, `JWT_SECRET`, `FRONTEND_ORIGINS`, `AI_SERVICE_URL`,
  `AI_SERVICE_KEY`. Secrets go in the service settings, never in the code.
