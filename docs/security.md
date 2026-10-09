# Security

What protects the API, layer by layer, and how to check it.

## Request pipeline

Every request goes through these layers, from the outside in:

| Layer | File | What it does |
|---|---|---|
| Request id | `app/request_context.py` | Gives each request an `X-Request-ID` (or keeps a safe one from the caller), logs method, path, status and time, never the query string or body |
| Body limit | `app/body_limit.py` | Refuses bodies over 1 MB with 413, also when they arrive without `Content-Length` |
| Rate limit | `app/rate_limit.py` | Per client IP, sliding window, 429 + `Retry-After` |
| Security headers | `app/security_headers.py` | `nosniff`, `DENY`, no referrer, strict CSP, `Permissions-Policy`, COOP/CORP, HSTS over HTTPS |
| CORS | `app/main.py` | Only the origins in `FRONTEND_ORIGINS`, only the methods and headers the frontend uses |
| Errors | `app/request_context.py` | Unexpected errors answer `500 {"detail": "Internal server error", "request_id": ...}`; the details only go to the log |

### Rate limits

| Route | Limit per IP |
|---|---|
| `POST /auth/register` | 5 per minute |
| `POST /auth/login` | 10 per minute (plus the 5-failure account lockout) |
| `POST /auth/refresh` | 30 per minute |
| `POST /auth/password` | 5 per 5 minutes |
| `POST /projects/{id}/ai...` | 20 per minute |
| Everything | 300 per minute |

Behind Render's proxy set `TRUSTED_PROXY_HOPS=1` so the real client IP is used. The counters live in
memory: with several instances, move them to a shared store (Redis).

## Accounts and tokens

- Passwords: salted scrypt, compared in constant time. Unknown emails take as long as wrong passwords.
- Password policy (`app/auth/password_policy.py`): 8–128 characters, not a common password, not only
  numbers, at least 4 different characters, and it cannot contain the email name or the username.
- `POST /auth/password` changes the password and revokes every refresh token of the account.
- Lockout: 5 failed logins per email or 20 per IP in 15 minutes. The failed attempt is committed before
  answering 401, so the count survives the rolled-back request.
- Access tokens: JWT HS256, 15 minutes, with `iss`, `aud` (`2d-engine-api`), `nbf`, `exp` and a `jti` that is
  revoked on logout. 5 seconds of clock leeway.
- Refresh tokens: random, stored as SHA-256 hashes, rotated on each use; reusing an old one revokes the
  whole login family. See [tokens.md](tokens.md).
- Backend → AI: 60-second JWT signed with `AI_SERVICE_KEY`, audience `ai-service`, single use.

## Configuration checks

`app/config.py` runs at start-up. With `ENVIRONMENT=production` the API **refuses to start** if:

- `JWT_SECRET` or `AI_SERVICE_KEY` is missing, shorter than 32 characters, not random enough or still the
  value from `.env.example`;
- `DATABASE_URL` is missing;
- `FRONTEND_ORIGINS` contains `*` or an `http://` site, or `AI_SERVICE_URL` is not `https://`.

In production `/docs` and `/openapi.json` are not published. In development the same problems are only
logged as warnings.

Generate secrets with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Data

- Every project query filters by the owner: another user's project answers 404, not 403.
- SQL is always parameterised (`%s`), never built from user input.
- Everything the AI returns is validated again (kinds, world bounds, at most one player).

## Checking it

```powershell
python -m pytest tests/test_security.py -v   # the security layer
pip install pip-audit; pip-audit -r requirements.txt   # known vulnerabilities in dependencies
```

CI runs both on every push.
