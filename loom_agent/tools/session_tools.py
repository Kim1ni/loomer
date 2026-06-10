from google.adk.tools import ToolContext

def increment_stuck_count(context: ToolContext) -> dict:
    """Increments the stuck count for the current task."""
    tasks = context.state.get("tasks", [])
    index = context.state.get("current_task_index", 0)
    for task in tasks:
        if task["index"] == index:
            task["stuck_count"] = task.get("stuck_count", 0) + 1
    context.state["tasks"] = tasks
    return {"status": "success"}

def get_stuck_count(context: ToolContext) -> int:
    """Returns the stuck count for the current task."""
    tasks = context.state.get("tasks", [])
    index = context.state.get("current_task_index", 0)
    for task in tasks:
        if task["index"] == index:
            return task.get("stuck_count", 0)
    return 0


def log_debug_note(context: ToolContext, note: str) -> dict:
    """Logs a debugging note against the current task. Use when the user discovers something while debugging."""
    tasks = context.state.get("tasks", [])
    index = context.state.get("current_task_index", 0)
    for task in tasks:
        if task["index"] == index:
            task.setdefault("debug_notes", []).append(note)
    context.state["tasks"] = tasks
    return {"status": "success", "note": note}


def get_debug_notes(context: ToolContext) -> list:
    """Returns all debug notes for the current task."""
    tasks = context.state.get("tasks", [])
    index = context.state.get("current_task_index", 0)
    for task in tasks:
        if task["index"] == index:
            return task.get("debug_notes", [])
    return []


def capture_idea(context: ToolContext, idea: str) -> dict:
    """Captures a loose idea mid-session and slots it into the project idea backlog."""
    ideas = context.state.get("ideas", [])
    ideas.append(idea)
    context.state["ideas"] = ideas
    return {"status": "success", "total_ideas": len(ideas)}


def get_ideas(context: ToolContext) -> list:
    """Returns all captured ideas for the current project."""
    return context.state.get("ideas", [])
