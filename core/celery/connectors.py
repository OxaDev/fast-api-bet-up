from celery import Celery

import api  # noqa: F401
import db  # noqa: F401
from core import env
from core.celery.tasks import task_root_list

celery_main_app = Celery("worker", broker=env.CELERY_MAIN_BROKER_URL, backend=env.CELERY_MAIN_RESULT_BACKEND)

celery_main_app.autodiscover_tasks(task_root_list)

celery_main_app.conf.update(
    # Time configuration
    timezone="UTC",  # Use UTC as timezone
    enable_utc=True,  # Enable UTC support
    # RedBeat configuration (scheduler)
    beat_scheduler="redbeat.RedBeatScheduler",  # Use RedBeat as scheduler
    redbeat_redis_url=env.REDIS_REDBEAT_URL,  # Redis URL for RedBeat
    redbeat_key_prefix="redbeat:",  # Redis key prefix for RedBeat
    redbeat_lock_key="redbeat:lock",  # Redis lock key (prevents double execution)
    redbeat_lock_timeout=30,  # Max lock duration in seconds
    # Beat configuration
    beat_max_loop_interval=5,  # Max interval between task checks (in seconds)
    beat_schedule={},  # Empty schedule by default, tasks are added dynamically
)
