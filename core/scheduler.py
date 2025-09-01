from apscheduler.schedulers.blocking import BlockingScheduler

from core.tasks import print_salut


def start_scheduler():
    scheduler = BlockingScheduler()
    # Envoie la tâche sur la queue "default"
    scheduler.add_job(lambda: print_salut.apply_async(queue="default"), "interval", minutes=1)
    scheduler.start()


if __name__ == "__main__":
    start_scheduler()
