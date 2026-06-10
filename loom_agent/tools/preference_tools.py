from typing import Any
from google.adk.tools import ToolContext


def set_user_name(context: ToolContext, name: str) -> dict[str, Any]:
    """Sets the user's name. E.g. "John Doe" """
    context.state["user:user_name"] = name
    return dict(
        status="success",
        message=f"Successfully saved the user's name as {name}"
    )

def get_user_name(context: ToolContext) -> dict[str, Any]:
    """Returns the user's name."""
    user_name = context.state.get("user:user_name", None)

    if not user_name:
        return dict(
            status="error",
            message="User name not set. Please set the user name first."
        )
    return dict(
        status="success",
        data=user_name
    )



def set_user_goal(context: ToolContext, goal: str) -> dict[str, Any]:
    """Sets the user's goal. E.g. "I want to build a birdhouse" """
    context.state["user_goal"] = goal
    return dict(
        status="success",
        message=f"Successfully saved the user's goal as {goal}"
    )

def get_user_goal(context: ToolContext) -> dict[str, Any]:
    """Returns the user's goal."""
    user_goal = context.state.get("user_goal", None)
    if not user_goal:
        return dict(
            status="error",
            message="User goal not set. Please set the user goal first."
        )
    return dict(
        status="success",
        data=user_goal
    )


def set_domain(context: ToolContext, domain: str) -> dict[str, Any]:
    """Sets the user's domain. E.g. "woodworking"," music", "programming" """
    context.state["domain"] = domain
    return dict(
        status="success",
        message=f"Successfully saved the user's domain as {domain}"
    )

def get_domain(context: ToolContext) -> dict[str, Any]:
    """Returns the user's domain."""
    domain = context.state.get("domain", None)
    if not domain:
        return dict(
            status="error",
            message="User domain not set. Please set the user domain first."
        )
    return dict(
        status="success",
        data=domain
    )



def set_experience_level(context: ToolContext, level: str) -> dict[str, Any]:
    """Sets the user's experience level. E.g. "beginner", "intermediate", "advanced" """
    context.state["experience_level"] = level
    return dict(
        status="success",
        message=f"Successfully saved the user's experience level as {level}"
    )

def get_experience_level(context: ToolContext) -> dict[str, Any]:
    """Returns the user's experience level."""
    experience_level = context.state.get("experience_level", None)
    if not experience_level:
        return dict(
            status="error",
            message="User experience level not set. Please set the user experience level first."
        )
    return dict(
        status="success",
        data=experience_level
    )



def set_preferred_resource_types(context: ToolContext, resources: list[str]) -> dict[str, Any]:
    """Sets the user's preferred resource types. E.g. ["YouTube", "book", "website", "article", "podcast"]"""
    context.state["user:preferred_resource_types"] = resources
    return dict(
        status="success",
        message=f"Successfully saved the user's preferred resource types as {resources}"
    )

def get_preferred_resource_types(context: ToolContext) -> dict[str, Any]:
    """Returns the user's preferred resource types."""
    preferred_resource_types = context.state.get("user:preferred_resource_types", [])
    return dict(
        status="success",
        data=preferred_resource_types
    )
