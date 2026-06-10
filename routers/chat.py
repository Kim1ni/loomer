from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from google.genai.types import Content, Part

import json

from pydantic import BaseModel

from google.adk.apps import App
from google.adk.apps.compaction import EventsCompactionConfig
from google.adk.plugins import LoggingPlugin
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from loom_agent.agent import root_agent

import uuid

from typing import AsyncGenerator

router = APIRouter(prefix="/loom/chat", tags=["Chat"])

APP_NAME="loom_app"
session_service = InMemorySessionService()
loom_app = App(
    name=APP_NAME,
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=5,
        overlap_size=1
    ),
    plugins=[
        LoggingPlugin()
    ]
)

runner = Runner(
    app=loom_app,
    session_service=session_service,
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "default-user"

def _sse(event: str, data: dict) -> str:
    """A simple helper to yield events cleanly"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

async def _stream(request: ChatRequest) -> AsyncGenerator[str, None]:
    session_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"

    existing = await session_service.get_session(
        app_name=APP_NAME,
        user_id=request.user_id,
        session_id=session_id,
    )
    if existing is None:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=request.user_id,
            session_id=session_id,
        )

    yield _sse("session", {"session_id": session_id, "user_id": request.user_id})

    try:
        async for event in runner.run_async(
            new_message=Content(parts=[Part(text=request.message)]),
            session_id=session_id,
            user_id=request.user_id,
        ):
            author = event.author or "unknown"

            for call in event.get_function_calls():
                yield _sse("tool_call", {
                    "author": author,
                    "id": call.id,
                    "name": call.name,
                    "args": dict(call.args) if call.args else {},
                })

            for resp in event.get_function_responses():
                yield _sse("tool_result", {
                    "author": author,
                    "id": resp.id,
                    "name": resp.name,
                    "response": resp.response,
                })

                # INTERCEPT: If the save_project tool was called successfully, emit our custom event
                if resp.name == "save_project" and isinstance(resp.response, dict) and resp.response.get("status") == "success":
                    project_id = resp.response.get("data")
                    if project_id:
                        yield _sse("project_created", {
                            "projectId": project_id
                        })

            if event.content and event.content.parts:
                text = "".join(
                    p.text for p in event.content.parts
                    if getattr(p, "text", None)
                )
                if text and author != "user":
                    yield _sse("text", {
                        "author": author,
                        "text": text,
                        "partial": bool(event.partial),
                    })

            if event.error_message:
                yield _sse("error", {
                    "author": author,
                    "code": event.error_code,
                    "message": event.error_message,
                })

    except Exception as e:
        yield _sse("error", {"author": "server", "message": str(e)})

    yield _sse("done", {"session_id": session_id})

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(_stream(request), media_type="text/event-stream")
