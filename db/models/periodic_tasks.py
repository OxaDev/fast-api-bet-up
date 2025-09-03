import uuid
from datetime import timedelta

from sqlalchemy import JSON, Column, DateTime, Integer, String

from db.config import Base


class PeriodicTask(Base):
    __tablename__ = "periodic_task"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=uuid.uuid4(), nullable=False, unique=True)
    task_name = Column(String(255), nullable=False)
    task_params = Column(JSON, nullable=True)
    task_queue = Column(String(255), nullable=False)
    interval = Column(Integer, nullable=False)
    last_run = Column(DateTime, default=None, nullable=True)

    def __repr__(self):
        return f"<PeriodicTask(id={self.id}, uuid={self.uuid}, interval=every {self.interval}s)>"

    @property
    def next_run(self):
        return self.last_run + timedelta(seconds=self.interval)
