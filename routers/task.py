from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from loom_agent.shared.models import Task
from loom_agent.shared.db import db

router = APIRouter()
projects_collection = db["projects"]

@router.get("/loom/{project_id}/tasks", response_model=List[Task])
def get_tasks(user_id: str, project_id: str):
    doc = projects_collection.find_one({"_id": ObjectId(project_id), "user_id": user_id}, {"tasks": 1})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    return doc.get("tasks", [])

@router.post("/{project_id}/tasks")
def add_task(user_id: str, project_id: str, task: Task):
    projects_collection.update_one(
        {"_id": ObjectId(project_id), "user_id": user_id},
        {"$push": {"tasks": task.model_dump()}}
    )
    return {"status": "success"}

@router.get("/{project_id}/tasks/{task_index}", response_model=Task)
def get_task_by_id(user_id: str, project_id: str, task_index: int):
    # Retrieve just the specific task using MongoDB aggregation/projection
    doc = projects_collection.find_one(
        {"_id": ObjectId(project_id), "user_id": user_id, "tasks.index": task_index},
        {"tasks.$": 1}
    )
    if not doc or "tasks" not in doc:
        raise HTTPException(status_code=404, detail="Task not found")
    return doc["tasks"]

@router.put("/{project_id}/tasks/{task_index}")
def update_task(user_id: str, project_id: str, task_index: int, task: Task):
    # The positional operator $ updates the specific array element matched in the query
    projects_collection.update_one(
        {"_id": ObjectId(project_id), "user_id": user_id, "tasks.index": task_index},
        {"$set": {"tasks.$": task.model_dump()}}
    )
    return {"status": "success"}

@router.delete("/{project_id}/tasks/{task_index}")
def delete_task(user_id: str, project_id: str, task_index: int):
    projects_collection.update_one(
        {"_id": ObjectId(project_id), "user_id": user_id},
        {"$pull": {"tasks": {"index": task_index}}}
    )
    return {"status": "success"}