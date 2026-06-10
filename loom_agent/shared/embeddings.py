from sentence_transformers import SentenceTransformer

from shared.consts import EMBEDDING_MODEL
from shared.db import db
import time

model = SentenceTransformer(
    model_name_or_path=EMBEDDING_MODEL,
    cache_folder="./model_cache"
)

def embed(text: str) -> list[float]:
    """Converts text to a vector embedding."""
    return model.encode(text).tolist()


def embed_many(texts: list[str]) -> list[list[float]]:
    """Converts a list of texts to vector embeddings in a single batched call."""
    return model.encode(texts).tolist()


def store_chunks(collection_name: str, source_id: str, chunks: list[dict]):
    """Stores chunks in MongoDB if not already stored."""
    col = db[collection_name]
    if col.find_one({"source_id": source_id}):
        return
    col.insert_many(chunks)

    # Block progress for a few seconds to let Atlas process the asynchronous queue
    # Adjust time based on chunk count size
    time.sleep(2.5)


def query_chunks(collection_name: str, source_id: str, task_description: str, index_name: str) -> dict | None:
    """Finds the most relevant chunk for a task description."""
    col = db[collection_name]
    results = list(col.aggregate([{
        "$vectorSearch": {
            "index": index_name,
            "path": "embedding",
            "queryVector": embed(task_description),
            "numCandidates": 50,
            "limit": 3,
            "filter": {"source_id": source_id}
        }
    }]))

    if not results:
        return None

    best_match_text = results[0]["text"]

    results.sort(key=lambda x: x["start"])
    start = results[0]["start"]
    last = results[-1]
    end = last["start"] + last.get("duration", 0)

    return {
        "start": int(start),
        "end": int(end),
        "text_preview": best_match_text
    }