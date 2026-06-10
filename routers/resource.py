from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from loom_agent.shared.models import Resource
from loom_agent.shared.db import db

router = APIRouter()
projects_collection = db["projects"]

@router.get("/loom/{project_id}/resources", response_model=List[Resource])
def get_resources(user_id: str, project_id: str):
    doc = projects_collection.find_one({"_id": ObjectId(project_id), "user_id": user_id}, {"resources": 1})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    return doc.get("resources", [])

@router.post("/{project_id}/resources")
def add_resource(user_id: str, project_id: str, resource: Resource):
    projects_collection.update_one(
        {"_id": ObjectId(project_id), "user_id": user_id},
        {"$push": {"resources": resource.model_dump()}}
    )
    return {"status": "success"}

@router.get("/{project_id}/resources/{resource_title}", response_model=Resource)
def get_resource_by_id(user_id: str, project_id: str, resource_title: str):
    doc = projects_collection.find_one(
        {"_id": ObjectId(project_id), "user_id": user_id, "resources.title": resource_title},
        {"resources.$": 1}
    )
    if not doc or "resources" not in doc:
        raise HTTPException(status_code=404, detail="Resource not found")
    return doc["resources"]

@router.put("/{project_id}/resources/{resource_title}")
def update_resource(user_id: str, project_id: str, resource_title: str, resource: Resource):
    projects_collection.update_one(
        {"_id": ObjectId(project_id), "user_id": user_id, "resources.title": resource_title},
        {"$set": {"resources.$": resource.model_dump()}}
    )
    return {"status": "success"}

@router.delete("/{project_id}/resources/{resource_title}")
def delete_resource(user_id: str, project_id: str, resource_title: str):
    projects_collection.update_one(
        {"_id": ObjectId(project_id), "user_id": user_id},
        {"$pull": {"resources": {"title": resource_title}}}
    )
    return {"status": "success"}