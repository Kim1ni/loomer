import os
from dotenv import load_dotenv

load_dotenv()

# AI AGENT MODEL
AGENT_MODEL = "gemini-flash-latest"

# EMBEDDING MODEL FOR SEMANTIC SEARCH
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# URI TO MONGODB
MONGODB_URI = os.environ.get('MONGODB_URI')