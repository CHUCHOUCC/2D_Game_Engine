"""Checks the security-relevant settings before the API starts.

In production (ENVIRONMENT=production) a weak or missing secret stops the
start-up instead of running an insecure service. In development the same
problems are only logged as warnings.
"""
import logging
import os

logger = logging.getLogger("app.config")

MIN_SECRET_LENGTH = 32
# Values copied from .env.example must never reach production.
PLACEHOLDER_MARKERS = ("change-me", "changeme", "example", "secret-here", "the-same")


class InsecureConfigurationError(RuntimeError):
    """A setting would make the service insecure."""


def is_production(env=os.environ) -> bool:
    return env.get("ENVIRONMENT", "development").strip().lower() == "production"


def _weak_secret(name: str, value: str) -> list:
    if not value:
        return [f"{name} is not set"]
    problems = []
    if len(value) < MIN_SECRET_LENGTH:
        problems.append(f"{name} must have at least {MIN_SECRET_LENGTH} characters")
    if any(marker in value.lower() for marker in PLACEHOLDER_MARKERS):
        problems.append(f"{name} still has the example value")
    if len(set(value)) < 10:
        problems.append(f"{name} is not random enough")
    return problems


def configuration_problems(env=os.environ) -> list:
    """Every problem found in the environment, as readable sentences."""
    problems = []
    problems += _weak_secret("JWT_SECRET", env.get("JWT_SECRET", ""))
    if env.get("AI_SERVICE_URL"):
        problems += _weak_secret("AI_SERVICE_KEY", env.get("AI_SERVICE_KEY", ""))
    if not env.get("DATABASE_URL"):
        problems.append("DATABASE_URL is not set")
    origins = [o.strip() for o in env.get("FRONTEND_ORIGINS", "").split(",") if o.strip()]
    if "*" in origins:
        problems.append("FRONTEND_ORIGINS must list the allowed sites, not '*'")
    if is_production(env):
        insecure = [o for o in origins if not o.startswith("https://")]
        if insecure:
            problems.append(f"FRONTEND_ORIGINS must use https in production: {', '.join(insecure)}")
        if env.get("AI_SERVICE_URL", "").startswith("http://"):
            problems.append("AI_SERVICE_URL must use https in production")
    return problems


def check_configuration(env=os.environ) -> list:
    """Raise in production if anything is insecure; otherwise log and return the problems."""
    problems = configuration_problems(env)
    if problems and is_production(env):
        raise InsecureConfigurationError("Insecure configuration: " + "; ".join(problems))
    for problem in problems:
        logger.warning("Configuration: %s", problem)
    return problems
