from celery import Celery

import api  # noqa: F401
import db  # noqa: F401
from core import env
from core.celery.tasks import task_root_list

celery_main_app = Celery("worker", broker=env.CELERY_MAIN_BROKER_URL, backend=env.CELERY_MAIN_RESULT_BACKEND)

celery_main_app.autodiscover_tasks(task_root_list)
