import time
from typing import Dict, Optional, List, Any
from server.tasks.task_models import DevelopmentPlan, TaskItem, TaskStatus

class TaskManager:
    """Manages structured development plans and task states for the product layer."""

    def __init__(self):
        self.active_plans: Dict[str, DevelopmentPlan] = {}

    def create_plan(self, session_id: str, title: str, requirement: str, tasks_data: List[dict]) -> DevelopmentPlan:
        tasks = []
        for t in tasks_data:
            tasks.append(TaskItem(
                title=t.get("title", "Task"),
                description=t.get("description", ""),
                dependencies=t.get("dependencies", []),
                files_affected=t.get("files_affected", [])
            ))

        plan = DevelopmentPlan(title=title, requirement=requirement, tasks=tasks)
        self.active_plans[session_id] = plan
        return plan

    def get_plan(self, session_id: str) -> Optional[DevelopmentPlan]:
        return self.active_plans.get(session_id)

    def update_task_status(
        self,
        session_id: str,
        task_id: str,
        status: TaskStatus,
        error_message: Optional[str] = None
    ) -> Optional[TaskItem]:
        plan = self.active_plans.get(session_id)
        if not plan:
            return None

        for task in plan.tasks:
            if task.id == task_id or task.title.lower() in task_id.lower():
                task.status = status
                if status == TaskStatus.IN_PROGRESS and not task.started_at:
                    task.started_at = time.time()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.completed_at = time.time()
                if error_message:
                    task.error_message = error_message
                return task
        return None
