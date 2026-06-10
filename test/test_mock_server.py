import warnings
import sys
import os

# Ensure the root project directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Temporarily suppress the starlette deprecation warning before the import happens
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fastapi.testclient import TestClient

from test.mock_main import app

client = TestClient(app)

def test_mock_chat():
    with client.stream("POST", "/loom/chat/stream", json={"message": "hello test"}) as response:
        assert response.status_code == 200
        
        full_text = ""
        for chunk in response.iter_text():
            full_text += chunk
            
        assert "event: session" in full_text
        assert "mock response" in full_text
        assert "event: project_created" in full_text
        assert "event: done" in full_text

if __name__ == "__main__":
    print("Running tests...")
    test_mock_chat()
    print("Test passed successfully!")
