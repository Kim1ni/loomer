from typing import Any
from google.adk.tools import ToolContext


def set_current_phase_index(context: ToolContext, index: int) -> dict[str, Any]:
    """Sets the user's current phase index. E.g., 1, 2, 3"""
    context.state["current_phase_index"] = index
    return dict(
        status="success",
        message=f"Successfully set the current phase index to {index}"
    )

def get_current_phase_index(context: ToolContext) -> dict[str, Any]:
    """Returns the user's current phase index."""
    current_phase_index =  context.state.get("current_phase_index", 0)
    if not current_phase_index:
        return dict(
            status="error",
            message="Current phase index not set. Please set the current phase index first."
        )
    return dict(
        status="success",
        data=current_phase_index
    )


def save_phases(context: ToolContext, phases: list[str]) -> dict[str, Any]:
    """Saves the generated phases to session state."""
    context.state["phases"] = phases
    context.state["current_phase_index"] = 0
    return dict(
        status="success",
        message=f"Successfully saved {len(phases)} phases"
    )

def is_phase_complete(context: ToolContext) -> dict[str, Any]:
    """Checks whether the current phase is complete."""
    tasks = context.state.get("tasks", [])
    current_phase_index = context.state.get("current_phase_index", 0)
    phases = context.state.get("phases", [])
    
    if not phases or current_phase_index >= len(phases):
        return dict(status="error", message="No valid phase to check.")
        
    current_phase = phases[current_phase_index]
    
    phase_tasks = [t for t in tasks if t.get("phase") == current_phase]
    if not phase_tasks:
        return dict(status="success", data=False)
        
    all_complete = all(t.get("is_complete", False) for t in phase_tasks)
    return dict(status="success", data=all_complete)
