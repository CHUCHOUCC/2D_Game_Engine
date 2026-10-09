# Tokens

Three kinds of token travel through the system. None of them is ever stored in plain text.

| Token | Who gets it | Format | Lifetime | Stored as |
|---|---|---|---|---|
| Access token | The frontend, after login | JWT HS256 signed with `JWT_SECRET` | 15 minutes | Only its id (`jti`) when revoked |
| Refresh token | The frontend, after login | 43 random URL-safe characters | 7 days, rotated on every use | SHA-256 hash in `refresh_tokens` |
| Service token | The backend, on every call to the AI service | JWT HS256 signed with `AI_SERVICE_KEY`, audience `ai-service` | 60 seconds | Not stored |

## Login flow

```
POST /auth/login {email, password}
  -> 5 failed attempts in 15 min?            429
  -> wrong email or password (same answer)   401
  -> {access_token, refresh_token, token_type: "bearer", expires_in: 900}

Any protected route:  Authorization: Bearer <access_token>
  -> signature, issuer, expiry and type checked; jti not revoked

POST /auth/refresh {refresh_token}
  -> new pair; the old refresh token is marked as replaced
  -> using a replaced token again = stolen copy: the whole login family is revoked

POST /auth/logout {refresh_token?}   revokes the access token and that login family
POST /auth/logout-all               revokes every refresh token of the account
```

## Access token claims

```json
{ "sub": "42", "jti": "9f1c...", "iss": "2d-engine-backend", "type": "access",
  "roles": ["creator"], "iat": 1760000000, "exp": 1760000900 }
```

## Service token claims (backend -> AI service)

```json
{ "iss": "2d-engine-backend", "aud": "ai-service", "sub": "backend", "scope": "ai",
  "jti": "c0ffee...", "iat": 1760000000, "exp": 1760000060 }
```

The raw `AI_SERVICE_KEY` never leaves the backend; only signed tokens do.

## Housekeeping

`python -m app.maintenance` deletes revoked access-token ids that have expired, refresh
tokens older than 30 days past expiry and login attempts older than a week.
