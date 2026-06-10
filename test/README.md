# Tests and Mocking

This directory contains testing utilities and mock implementations for the Loomer project.

## Mock Server (`mock_main.py`)

When developing or testing the client interface, you might not want to consume actual AI tokens or interact with the real Gemini model. The `mock_main.py` script provides a fully functional mocked version of the main FastAPI application.

It routes standard API requests to your real routers (`project`, `task`, `resource`) but intercepts requests to the expensive `/loom/chat/stream` endpoint. Instead of triggering the real LLM agent, it simulates Server-Sent Events (SSE) including fake text streams, tool calls, and tool results.

### How to Run the Mock Server

Because `test` is a built-in Python module, running `uvicorn test.mock_main:app` can sometimes cause import conflicts. The safest way to run the mock server is to change into the `test` directory and run it directly:

```sh
cd test
uvicorn mock_main:app --reload --port 8000
```

### Testing with the Client

Once the mock server is running, open a new terminal tab and connect to it using your existing client application from the root directory:

```sh
python client.py --url http://127.0.0.1:8000/loom/chat/stream
```

### Running Automated Tests

To run the automated tests (such as `test_mock_server.py`), you can use `pytest` from the root directory:

```sh
uv run pytest test/
```