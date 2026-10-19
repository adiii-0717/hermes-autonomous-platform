import uuid
import time
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    TESTING = "TESTING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

class TaskItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = Field(default_factory=list)
    files_affected: List[str] = Field(default_factory=list)
    commands: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class DevelopmentPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    requirement: str
    tasks: List[TaskItem] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)

    def progress_percentage(self) -> float:
        if not self.tasks:
            return 0.0
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return round((completed / len(self.tasks)) * 100, 1)
