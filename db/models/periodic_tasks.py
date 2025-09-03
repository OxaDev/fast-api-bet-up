import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from db.config import Base


class PeriodicTask(Base):
    __tablename__ = "periodic_task"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=uuid.uuid4(), nullable=False, unique=True)
    interval = Column(Integer, nullable=False)
    last_run = Column(DateTime, default=None, nullable=True)

    def __repr__(self):
        return f"<PeriodicTask(id={self.id}, uuid={self.uuid}, interval=every {self.interval}s)>"

    @property
    def next_run(self):
        return self.last_run + timedelta(seconds=self.interval)


def update_last_run_date(session: Session, uuid: str) -> PeriodicTask:
    task = session.query(PeriodicTask).filter(PeriodicTask.uuid == uuid).first()
    if not task:
        raise ValueError(f"Task with uuid {uuid} not found")

    task.last_run = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
