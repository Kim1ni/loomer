from typing import Generic, TypeVar, Any

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class TranscriptChunk(BaseModel):
    text: str
    start: float
    duration: float
    model_config = ConfigDict(extra='allow')


class YouTubeVideoResult(BaseModel):
    video_id: str
    title: str
    description: str
    thumbnail: str
    model_config = ConfigDict(extra='allow')


class TranscriptSegment(BaseModel):
    video_id: str
    text: str
    start: float
    end: float
    model_config = ConfigDict(extra='allow')


class Resource(BaseModel):
    title: str
    url: str
    type: str
    timestamp_start: int | None = None
    timestamp_end: int | None = None
    text_preview: str | None = None
    model_config = ConfigDict(extra='allow')


class Task(BaseModel):
    index: int
    phase: str
    title: str
    description: str
    is_complete: bool = False
    resources: list[Resource] = []
    model_config = ConfigDict(extra='allow')


class Project(BaseModel):
    id: str
    user_name: str
    goal: str
    domain: str
    phases: list[str] = []
    tasks: list[Task] = []
    model_config = ConfigDict(extra='allow')


class ToolResult(BaseModel, Generic[T]):
    status: str
    message: str | None = None
    data: T | None = None
    model_config = ConfigDict(extra='allow')
