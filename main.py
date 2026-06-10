from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from loom_agent.agent import root_agent
from routers import project, task, resource, chat

app = FastAPI(title="Loomer App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(project.router)
app.include_router(task.router, prefix="/users/{user_id}/projects", tags=["Tasks"])
app.include_router(resource.router, prefix="/users/{user_id}/projects", tags=["Resources"])

@app.get("/")
async def root():
    return {"status": "ok", "agent": root_agent.name}
