from typing import Any
from google.adk.tools import ToolContext


def save_tasks(context: ToolContext, tasks: list[dict]) -> dict[str, Any]:
    """Saves generated tasks for the current phase."""
    existing = context.state.get("tasks", [])
    existing.extend(tasks)
    context.state["tasks"] = existing
    context.state["current_task_index"] = 0
    return {"status": "success", "tasks": tasks}

def update_task_with_resources(context: ToolContext, task_index: int, resources: list[dict]) -> dict[str, Any]:
    """Updates a task with the provided resources."""
    tasks = context.state.get("tasks", [])
    for task in tasks:
        if task.get("index") == task_index:
            task["resources"] = resources
            break
    context.state["tasks"] = tasks
    return dict(status="success", message="Task updated successfully")

def set_current_task_index(context: ToolContext, index: int) -> dict[str, Any]:
    """Sets the user's current task index. E.g., 1, 2, 3"""
    context.state["current_task_index"] = index
    return dict(status="success", message=f"Task index set to {index}")

def increment_task_index(context: ToolContext) -> dict[str, Any]:
    """Increments/moves the user's current task index by 1."""
    current_index = context.state.get("current_task_index", 0)
    context.state["current_task_index"] = current_index + 1
    return dict(status="success", message="Task index incremented")

def get_current_task_index(context: ToolContext) -> dict[str, Any]:
    """Returns the user's current task index."""
    current_index = context.state.get("current_task_index", 0)
    return dict(status="success", data=current_index)

def mark_task_complete(context: ToolContext) -> dict[str, Any]:
    """Marks the current task as complete."""
    tasks = context.state.get("tasks", [])
    index = context.state.get("current_task_index", 0)
    for task in tasks:
        if task.get("index") == index:
            task["is_complete"] = True
    context.state["tasks"] = tasks
    return {"status": "success"}