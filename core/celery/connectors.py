from celery import Celery

import api  # noqa: F401
import db  # noqa: F401
from core import env
from core.celery.tasks import task_root_list

celery_main_app = Celery("worker", broker=env.CELERY_MAIN_BROKER_URL, backend=env.CELERY_MAIN_RESULT_BACKEND)

celery_main_app.autodiscover_tasks(task_root_list)

celery_main_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_scheduler="redbeat.RedBeatScheduler",
    redbeat_redis_url=env.REDIS_REDBEAT_URL,
    redbeat_key_prefix="redbeat:",
    redbeat_lock_key="redbeat:lock",
    redbeat_lock_timeout=30,
    beat_max_loop_interval=5,
    beat_schedule={},
)
