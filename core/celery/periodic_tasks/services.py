import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from redbeat import RedBeatSchedulerEntry
from sqlalchemy.ext.asyncio import AsyncSession

from core.celery.connectors import celery_main_app
from core.celery.queues import Queues
from db.models.periodic_tasks import PeriodicTask


@dataclass
class PeriodicTaskManager:
    db_session: AsyncSession

    async def create(
        self,
        task_name: str,
        interval: int,
        task_uuid: str | None = None,
        task_args: list | None = None,
        task_kwargs: dict | None = None,
        queue: Queues = Queues.DEFAULT,
    ) -> PeriodicTask:
        cleaned_args = [] if task_args is None else task_args
        cleaned_kwargs = {} if task_kwargs is None else task_kwargs
        cleaned_task_uuid = task_uuid if task_uuid is not None else str(uuid.uuid4())

        new_task = PeriodicTask(
            task_name=task_name,
            uuid=cleaned_task_uuid,
            interval=interval,
            task_params={"args": cleaned_args, "kwargs": cleaned_kwargs},
            task_queue=queue,
        )
        self.db_session.add(new_task)
        await self.db_session.commit()
        await self.db_session.refresh(new_task)
        await self._create_associated_entry(new_task)
        return new_task

    async def _delete_associated_entry(self, task: PeriodicTask) -> None:
        try:
            key = f"redbeat:{task.uuid}"
            entry = RedBeatSchedulerEntry.from_key(key, app=celery_main_app)
            entry.delete()
        except KeyError:
            pass

    async def _associated_entry_exists(self, task: PeriodicTask) -> bool:
        try:
            key = f"redbeat:{task.uuid}"
            RedBeatSchedulerEntry.from_key(key, app=celery_main_app)
            return True
        except KeyError:
            return False

    async def _create_associated_entry(self, task: PeriodicTask) -> None:
        await self._delete_associated_entry(task)

        entry = RedBeatSchedulerEntry(
            name=task.uuid,
            task=task.task_name,
            schedule=timedelta(seconds=task.interval),
            args=task.task_params.get("args", []),
            kwargs=task.task_params.get("kwargs", {}),
            app=celery_main_app,
            options={"queue": task.task_queue},
        )
        entry.save()

    async def delete(self, task: PeriodicTask) -> None:
        await self._delete_associated_entry(task)
        await self.db_session.delete(task)
        await self.db_session.commit()

    async def update_interval(self, task: PeriodicTask, new_interval: int) -> None:
        task.interval = new_interval
        await self._delete_associated_entry(task)
        await self._create_associated_entry(task)
        await self.db_session.commit()

    async def update_last_run_from_uuid(self, task_uuid: str) -> None:
        task = await self.db_session.query(PeriodicTask).filter(PeriodicTask.uuid == task_uuid).first()
        if task:
            task.last_run = datetime.now(timezone.utc)
            await self.db_session.commit()
