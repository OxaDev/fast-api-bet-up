import logging
import uuid
from datetime import timedelta

from fastapi import APIRouter
from redbeat import RedBeatSchedulerEntry

from core.celery.connectors import celery_main_app

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/beat", tags=["celery", "redbeat"])


@router.post("/create-task-check/")
async def create_task_check():
    try:
        # Préfixe redbeat: est géré automatiquement par RedBeat
        task_name = str(uuid.uuid4())
        logger.info(f"Creating task with name: {task_name}")

        entry = RedBeatSchedulerEntry(
            name=task_name,
            task="core.tasks.scheduled_task_check",
            schedule=timedelta(seconds=10),
            args=[],
            app=celery_main_app,
            options={"queue": "default"},
        )

        entry.save()
        # Récupération de la clé après la sauvegarde
        redis_key = entry.key

        return {
            "status": "success",
            "task_name": task_name,
            "redis_key": redis_key,  # Ajout de la clé Redis dans la réponse
            "schedule": "every 10 seconds",
        }
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}


@router.delete("/delete-task/{task_name}")
async def delete_task(task_name: str):
    try:
        key = f"redbeat:{task_name}"
        entry = RedBeatSchedulerEntry.from_key(key, app=celery_main_app)
        entry.delete()
        return {"status": "success", "message": f"Task '{task_name}' deleted"}
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}
