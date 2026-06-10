from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from loom_agent.shared.models import Project
from loom_agent.shared.db import db

projects_collection = db["projects"]

def format_project(doc: dict) -> dict | None:
    if not doc:
        return None
    doc["project_id"] = str(doc.pop("_id"))
    return doc

router = APIRouter(prefix="/loom/users/{user_id}/projects", tags=["Projects"])

@router.get("", response_model=List[Project])
def get_projects(user_id: str):
    cursor = projects_collection.find({"user_id": user_id})
    return [format_project(doc) for doc in cursor]

@router.post("")
def create_project(user_id: str, project: Project):
    project_dict = project.model_dump(exclude={"project_id"})
    project_dict["user_id"] = user_id
    projects_collection.insert_one(project_dict)
    return {"status": "success"}

@router.get("/{project_id}", response_model=Project)
def get_project_by_id(user_id: str, project_id: str):
    doc = projects_collection.find_one({"_id": ObjectId(project_id), "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    return format_project(doc)

@router.put("/{project_id}")
def update_project(user_id: str, project_id: str, project: Project):
    update_data = project.model_dump(exclude={"project_id"})
    result = projects_collection.update_one(
        {"_id": ObjectId(project_id), "user_id": user_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "success"}

@router.delete("/{project_id}")
def delete_project(user_id: str, project_id: str):
    projects_collection.delete_one({"_id": ObjectId(project_id), "user_id": user_id})
    return {"status": "success"}