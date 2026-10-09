import os

from fastapi import Depends

from app.ai_client import AiServiceClient
from app.database import database_connection
from .repository import AiModelRepository


def get_ai_models(connection=Depends(database_connection)) -> AiModelRepository:
    return AiModelRepository(connection)


def get_optional_ai_client() -> AiServiceClient | None:
    """The AI client, or None when the AI service is not configured.

    Learning after a run is best effort: the run is saved even without AI.
    """
    url = os.environ.get("AI_SERVICE_URL")
    key = os.environ.get("AI_SERVICE_KEY")
    if not url or not key:
        return None
    return AiServiceClient(url, key)
