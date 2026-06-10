# Loomer

Loomer is an AI-powered assistant and backend API built with FastAPI and the Google Agent Development Kit (ADK). It helps users brainstorm, plan, and manage projects, tasks, and resources.

## Project Structure

- `main.py`: The FastAPI application entrypoint. It ties together the different routers and middlewares.
- `api.py`: Configures the Google ADK AI Agent (`App`, `Runner`, and `SessionService`).
- `routers/`: Contains all the FastAPI route definitions.
  - `chat.py`: Server-Sent Events (SSE) streaming endpoint for communicating with the AI Agent.
  - `project.py`: CRUD operations for Projects.
  - `task.py`: CRUD operations for Tasks within a project.
  - `resource.py`: CRUD operations for Resources (e.g., YouTube videos, articles) within a project.
- `loom_agent/`: Contains the AI agent configuration, sub-agents, shared database connections, models, and tools.

## Prerequisites

- Python 3.10+
- MongoDB instance
- [YouTube Data API Key](https://developers.google.com/youtube/v3/getting-started) (for finding video resources)
- Google Gemini / Vertex API Key (for the LLM)

## Setup & Running

1. **Environment Variables**: Create a `.env` file in the root directory and add your keys:
   ```env
   MONGODB_URI=mongodb://localhost:27017/  # Or your MongoDB Atlas URI
   YOUTUBE_DATA_API_KEY=your_youtube_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

2. **Install Dependencies**:
   ```bash
   uv sync
   ```

3. **Run the Server**:
   Start the FastAPI development server using `uvicorn`:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

## API Documentation

Once the server is running, you can view the interactive OpenAPI documentation by visiting:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Core Endpoints

#### AI Chat
- `POST /chat/stream`: Send a message to the AI agent. Returns a stream of Server-Sent Events (SSE) including tool calls, tool results, and the AI's textual response.
  - Body: `{"message": "I want to build a birdhouse", "user_id": "user123", "session_id": "optional-session-id"}`

#### Projects (`/users/{user_id}/projects`)
- `GET /`: List all projects for a user.
- `POST /`: Create a new project.
- `GET /{project_id}`: Retrieve a specific project.
- `PUT /{project_id}`: Update project details.
- `DELETE /{project_id}`: Delete a project.

#### Tasks (`/users/{user_id}/projects/{project_id}/tasks`)
- `GET /`: List all tasks for a project.
- `POST /`: Add a task to a project.
- `GET /{task_index}`: Retrieve a specific task by its index.
- `PUT /{task_index}`: Update a specific task.
- `DELETE /{task_index}`: Remove a task from the project.

#### Resources (`/users/{user_id}/projects/{project_id}/resources`)
- `GET /`: List all saved resources for a project.
- `POST /`: Add a new resource.
- `GET /{resource_id}`: Retrieve a specific resource by its id.
- `PUT /{resource_id}`: Update a specific resource.
- `DELETE /{resource_id}`: Remove a resource.
