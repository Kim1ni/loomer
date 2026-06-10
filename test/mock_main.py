import sys
import os

# Ensure the root project directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import uuid
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# We import the other routers as they likely don't consume tokens directly,
# but we avoid importing the real chat router.
from routers import project, task, resource

app = FastAPI(title="Loomer App (Mocked)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "default-user"

def _sse(event: str, data: dict) -> str:
    """A simple helper to yield events cleanly"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

async def _mock_stream(request: ChatRequest) -> AsyncGenerator[str, None]:
    session_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
    
    yield _sse("session", {"session_id": session_id, "user_id": request.user_id})
    await asyncio.sleep(0.2)
    
    # Optional: Simulate a mock tool call just to test your client's rendering
    yield _sse("tool_call", {
        "author": "LoomAgent",
        "id": "mock_call",
        "name": "save_project",
        "args": {"query": request.message}
    })
    await asyncio.sleep(0.2)
    
    mock_project_id = str(uuid.uuid4())
    
    yield _sse("tool_result", {
        "author": "LoomAgent",
        "id": "mock_call",
        "name": "save_project",
        "response": {"status": "success", "message": f"Project saved with ID: {mock_project_id}", "project_id": mock_project_id}
    })
    await asyncio.sleep(0.1)
    
    # EMIT THE MOCK PROJECT CREATED EVENT
    yield _sse("project_created", {
        "projectId": mock_project_id
    })
    await asyncio.sleep(0.2)
    
    # Simulate streaming text
    response_text = f"This is a mock response to save tokens. You said: '{request.message}'."
    for word in response_text.split():
        yield _sse("text", {
            "author": "LoomAgent",
            "text": word + " ",
            "partial": True,
        })
        await asyncio.sleep(0.1)
        
    # Send the final non-partial text event
    yield _sse("text", {
        "author": "LoomAgent",
        "text": "",
        "partial": False,
    })

    yield _sse("done", {"session_id": session_id})

# Mount the mock chat router
@app.post("/loom/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    return StreamingResponse(_mock_stream(request), media_type="text/event-stream")

# Mount the real endpoints for the rest of your API
app.include_router(project.router)
app.include_router(task.router, prefix="/users/{user_id}/projects", tags=["Tasks"])
app.include_router(resource.router, prefix="/users/{user_id}/projects", tags=["Resources"])

@app.get("/")
async def root():
    return {"status": "ok", "agent": "MockLoomAgent"}
