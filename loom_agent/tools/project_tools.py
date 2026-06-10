import uuid
from typing import Any

from google.adk.tools import ToolContext

from shared.db import db as database


def set_project_id(context: ToolContext, project_id: str) -> dict[str, Any]:
    """Sets the current project ID in the context."""
    context.state["project_id"] = project_id
    return dict(status="success", message=f"Project ID set to {project_id}")


def get_project_id(context: ToolContext) -> dict[str, Any]:
    """Retrieves the current project ID from the context."""
    project_id = context.state.get("project_id")
    if project_id:
        return dict(status="success", data=project_id)
    return dict(status="error", message="Project ID not found in context.")


def get_current_project_state(context: ToolContext) -> dict[str, Any]:
    """Retrieves the full state of the current project from the database."""
    project_id = context.state.get("project_id")
    if not project_id:
        return dict(status="error", message="Project ID not set in context.")

    try:
        collection = database["projects"]
        project_state = collection.find_one({"id": project_id})

        if project_state:
            # Remove non-serializable BSON ObjectId
            if "_id" in project_state:
                del project_state["_id"]
            return dict(status="success", data=project_state)
        else:
            return dict(status="error", message="Project not found in database.")

    except Exception as e:
        return dict(status="error", message=str(e))


def save_project(context: ToolContext) -> dict[str, Any]:
    """
    Saves the user's project configurations into MongoDB.
    """
    user_name = context.state.get("user:user_name")
    goal = context.state.get("user_goal")
    domain = context.state.get("domain")

    if not all([user_name, goal, domain]):
        return dict(
            status="error",
            message="Missing required context information. Make sure name, goal, and domain are set."
        )

    phases = context.state.get("phases", [])
    tasks = context.state.get("tasks", [])

    project_id = str(uuid.uuid4())
    project_doc = {
        "id": project_id,
        "user_name": user_name,
        "goal": goal,
        "domain": domain,
        "phases": phases,
        "tasks": tasks
    }

    try:
        collection = database["projects"]
        collection.insert_one(project_doc)

        context.state["project_id"] = project_id
        # Include the project_id explicitly in the return payload so we can intercept it
        return dict(status="success", message=f"Project saved with ID: {project_id}", data=project_id)

    except Exception as e:
        return dict(status="error", message=str(e))


def update_project(context: ToolContext, changes: dict) -> dict[str, Any]:
    """Updates specific fields of the user's project configurations."""
    project_id = context.state.get("project_id")
    if not project_id:
        return dict(status="error", message="Project not found in context.")

    try:
        collection = database["projects"]

        result = collection.update_one(
            {"id": project_id},
            {"$set": changes}
        )

        if result.modified_count > 0:
            for key, value in changes.items():
                if key in ["user_name", "goal", "domain"]:
                     context.state[key] = value
                elif key == "phases":
                    context.state["phases"] = value
                elif key == "tasks":
                     context.state["tasks"] = value

            return dict(status="success", message="Project updated successfully.")
        else:
             return dict(status="error", message="No changes made.")

    except Exception as e:
        return dict(status="error", message=str(e))


def load_project(context: ToolContext, project_id: str) -> dict[str, Any]:
    """Loads a project from the database into the context state."""
    try:
        collection = database["projects"]
        project_state = collection.find_one({"id": project_id})

        if not project_state:
            return dict(status="error", message="Project not found.")

        # Load properties into context state
        context.state["project_id"] = project_id
        context.state["user:user_name"] = project_state.get("user_name", "")
        context.state["user_goal"] = project_state.get("goal", "")
        context.state["domain"] = project_state.get("domain", "")
        context.state["phases"] = project_state.get("phases", [])
        context.state["tasks"] = project_state.get("tasks", [])

        return dict(status="success", message=f"Project {project_id} loaded successfully.")
    except Exception as e:
        return dict(status="error", message=str(e))


def list_projects(context: ToolContext) -> dict[str, Any]:
    """Lists all available projects."""
    try:
        collection = database["projects"]
        
        projects = []
        for doc in collection.find({}, {"_id": 0, "id": 1, "goal": 1, "domain": 1, "user_name": 1}):
            projects.append(doc)
            
        return dict(status="success", data=projects)
    except Exception as e:
        return dict(status="error", message=str(e))


def get_progress_summary(context: ToolContext) -> dict[str, Any]:
    """Gets a high-level summary of the current project progress."""
    project_id = context.state.get("project_id")
    if not project_id:
        return dict(status="error", message="No active project in context.")
        
    goal = context.state.get("user_goal", "Unknown")
    domain = context.state.get("domain", "Unknown")
    
    phases = context.state.get("phases", [])
    tasks = context.state.get("tasks", [])
    
    completed_tasks = len([t for t in tasks if t.get("is_complete")])
    total_tasks = len(tasks)
    
    summary = {
        "id": project_id,
        "goal": goal,
        "domain": domain,
        "total_phases": len(phases),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "progress": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    }
    
    return dict(status="success", data=summary)