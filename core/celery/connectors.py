from celery import Celery

from core import env
from core.celery.tasks import task_root_list

celery_main_app = Celery("worker", broker=env.CELERY_MAIN_BROKER_URL, backend=env.CELERY_MAIN_RESULT_BACKEND)

celery_main_app.autodiscover_tasks(task_root_list)
