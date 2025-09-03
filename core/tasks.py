from celery import shared_task


@shared_task
def scheduled_task_check():
    print("Scheduled task check!")
