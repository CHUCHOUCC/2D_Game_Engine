# Database

PostgreSQL (Supabase in production). The schema lives in `migrations/` as numbered SQL files;
`python -m app.migrate` runs the ones the database has not seen yet and records them in
`schema_migrations`. Every file is idempotent (`if not exists`, `on conflict do nothing`).

**53 tables** in total (52 from the migrations + `schema_migrations`).

## Accounts and security (17)

| Table | What it holds |
|---|---|
| `users` | Account: username, email, salted scrypt hash, last login |
| `sessions` | Legacy opaque-token sessions (only cleaned by `app.maintenance`) |
| `roles`, `permissions`, `role_permissions`, `user_roles` | Role-based access (player, creator, admin) |
| `refresh_tokens` | Hash of each refresh token, its login family and rotation chain |
| `revoked_access_tokens` | JWT ids revoked before expiring (logout) |
| `login_attempts` | Every login attempt; 5 failures in 15 min lock the email |
| `password_reset_tokens`, `email_verification_tokens` | One-time token hashes |
| `api_keys` | Personal API keys (hash + prefix + scopes) |
| `service_clients` | Internal services that accept service tokens (the AI service) |
| `audit_logs` | Login, logout, token reuse and other security events |
| `user_profiles` | Display name, avatar, bio, country |
| `user_settings` | Theme (light/dark), language, grid, volumes |
| `editor_shortcuts` | Custom keyboard shortcuts |

## Projects and scenes (12)

| Table | What it holds |
|---|---|
| `projects` | Owner, name, scene (JSON array of objects) |
| `project_members` | Shared projects (owner, editor, viewer) |
| `project_versions` | Snapshot of the scene on every save; can be restored |
| `scenes`, `scene_layers`, `game_objects` | Normalised scene model (size, layers, objects) |
| `prefabs` | Objects saved for reuse |
| `tags`, `project_tags` | Labels for projects |
| `assets` | Uploaded files |
| `level_templates` | Starter scenes (empty, village) |
| `notifications` | Messages for a user |

## Game content and physics (9)

| Table | What it holds |
|---|---|
| `object_kinds` | player, box, wall, house, tree, spike, coin, enemy and their flags |
| `physics_materials` | Friction, bounce, density (stone, wood, flesh, metal) |
| `object_physics` | Arcade Physics body of each kind (static/dynamic, mass, drag) |
| `enemy_types` | Slime, skeleton, bat: health, speed, damage, behaviour |
| `texture_packs`, `textures`, `sprite_animations`, `tilesets`, `tiles` | The pixel-art pack |

## Play and AI learning (14)

| Table | What it holds |
|---|---|
| `play_sessions` | One run of a level: outcome, score, coins, enemies, damage, time, difficulty |
| `play_events` | What happened during a run (coin taken, hit...) |
| `player_stats` | Running totals per player |
| `high_scores` | Leaderboard per level |
| `achievements`, `user_achievements` | Achievements and who unlocked them |
| `ai_models` | What the AI learned per level (parameters JSON, samples seen) |
| `ai_training_samples` | Each learning step: features of the run and the reward |
| `ai_obstacle_rules` | Per-kind weights for placing obstacles |
| `ai_requests`, `ai_generations`, `ai_feedback` | Every AI call, what it produced and ratings |
| `app_settings`, `feature_flags` | Global configuration |

## Running it

```powershell
# production / Supabase (DATABASE_URL in .env)
python -m app.migrate

# throw-away local PostgreSQL for the SQL tests (no install needed, uses PGlite):
npx --yes @electric-sql/pglite-socket -p 54329 -m 4      # in another terminal
$env:DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:54329/postgres?sslmode=disable"
python -m app.migrate
$env:TEST_DATABASE_URL = $env:DATABASE_URL
python -m pytest
```

PGlite drops the connection after a SQL error, so the one test that provokes a
unique-key violation is skipped there; CI runs it against a real PostgreSQL 16.
