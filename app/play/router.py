from fastapi import APIRouter, Depends, HTTPException

from app.ai_client import AiServiceClient, AiServiceError
from app.ai_learning.dependencies import get_ai_models, get_optional_ai_client
from app.ai_learning.repository import AiModelRepository, difficulty_of
from app.auth.dependencies import current_user
from app.auth.user import User
from app.database import database_connection
from app.projects.router import get_repository, load_project
from .achievements import AchievementRepository, earned_codes
from .repository import PlayRepository
from .schemas import RunResult

router = APIRouter(tags=["play"])


def get_plays(connection=Depends(database_connection)) -> PlayRepository:
    return PlayRepository(connection)


def get_achievements(connection=Depends(database_connection)) -> AchievementRepository:
    return AchievementRepository(connection)


@router.post("/projects/{project_id}/plays", status_code=201)
def start_run(project_id: int, repo=Depends(get_repository), plays: PlayRepository = Depends(get_plays),
              models: AiModelRepository = Depends(get_ai_models), user: User = Depends(current_user)):
    """Start a run of the level. The answer says how hard the AI made it."""
    load_project(project_id, repo, user.id)
    difficulty = difficulty_of(models.get(project_id))
    return {"id": plays.start(project_id, user.id, difficulty), "difficulty": difficulty}


@router.post("/projects/{project_id}/plays/{play_id}/finish")
def finish_run(
    project_id: int,
    play_id: int,
    body: RunResult,
    repo=Depends(get_repository),
    plays: PlayRepository = Depends(get_plays),
    models: AiModelRepository = Depends(get_ai_models),
    user: User = Depends(current_user),
    ai_client: AiServiceClient | None = Depends(get_optional_ai_client),
    achievements: AchievementRepository = Depends(get_achievements),
):
    """Save the run, update the player's totals and let the AI learn from it."""
    load_project(project_id, repo, user.id)
    if plays.find_open(play_id, project_id, user.id) is None:
        raise HTTPException(status_code=404, detail="Run not found or already finished")
    plays.finish(play_id, body)
    plays.add_to_player_stats(user.id, body)
    plays.add_high_score(project_id, user.id, body.score)
    unlocked = achievements.unlock(user.id, earned_codes(body, plays.stats_of(user.id)))

    model = models.get(project_id)
    learning = {"learned": False, "difficulty": difficulty_of(model)}
    if ai_client is not None:
        try:
            reply = ai_client.learn(model["parameters"], body.summary())
        except AiServiceError:
            reply = None
        if reply is not None:
            model_id = models.save(project_id, reply["model"])
            reward = float(reply.get("reward", 0))
            models.add_sample(model_id, play_id, body.summary(), reward)
            learning = {
                "learned": True,
                "reward": reward,
                "difficulty": float(reply.get("difficulty", difficulty_of({"parameters": reply["model"]}))),
            }
    plays.record_event_summary(play_id, learning)
    return {**learning, "achievements": unlocked}


@router.get("/projects/{project_id}/leaderboard")
def leaderboard(project_id: int, repo=Depends(get_repository), plays: PlayRepository = Depends(get_plays),
                user: User = Depends(current_user)):
    load_project(project_id, repo, user.id)
    return [dict(row) for row in plays.leaderboard(project_id)]


@router.get("/me/stats")
def my_stats(plays: PlayRepository = Depends(get_plays), user: User = Depends(current_user)):
    row = plays.stats_of(user.id)
    if row is None:
        return {"games_played": 0, "games_won": 0, "total_score": 0, "best_score": 0,
                "coins_collected": 0, "enemies_defeated": 0, "deaths": 0, "play_time_ms": 0}
    return dict(row)


@router.get("/me/achievements")
def my_achievements(achievements: AchievementRepository = Depends(get_achievements),
                    user: User = Depends(current_user)):
    return [{**row, "unlocked_at": row["unlocked_at"].isoformat()} for row in map(dict, achievements.of_user(user.id))]
