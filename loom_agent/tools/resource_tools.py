import os
from typing import Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from youtube_transcript_api import YouTubeTranscriptApi, FetchedTranscriptSnippet

from shared.embeddings import embed_many, store_chunks, query_chunks
from shared.models import Resource, TranscriptChunk, YouTubeVideoResult

load_dotenv()

YOUTUBE_DATA_API_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_DATA_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY")
LANG_CODE = "en"

def search_youtube_video(task_description: str, lang_code=LANG_CODE) -> dict[str, Any]:
    """Searches YouTube for videos related to the task description."""
    params = {
        'part': 'snippet',
        'q': task_description,
        'type': 'video',
        'order': 'relevance',
        'maxResults': 5,
        'relevanceLanguage': lang_code,
        'key': YOUTUBE_DATA_API_KEY,
    }
    response = requests.get(YOUTUBE_DATA_API_URL, params=params)
    if response.status_code != 200:
        return dict(status="error", message=f"YouTube API error: {response.status_code} - {response.text}")

    items = response.json().get("items", [])
    if not items:
        return dict(status="error", message="No videos found for this task.")

    videos = [
        YouTubeVideoResult(
            video_id=item["id"]["videoId"],
            title=item["snippet"]["title"],
            description=item["snippet"]["description"],
            thumbnail=item["snippet"]["thumbnails"]["high"]["url"],
        )
        for item in items
    ]
    return dict(status="success", data=[v.model_dump() for v in videos])


def to_transcript_chunk(chunk: FetchedTranscriptSnippet) -> TranscriptChunk:
    return TranscriptChunk(
        text=chunk.text,
        start=chunk.start,
        duration=chunk.duration
    )


def get_youtube_video_transcript(video_id: str) -> dict[str, Any]:
    """Fetches the transcript of a YouTube video."""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=[LANG_CODE])
        chunks = list(map(to_transcript_chunk, transcript))
        return dict(status="success", data=[c.model_dump() for c in chunks])
    except Exception as e:
        return dict(status="error", message=str(e))


def store_transcript_chunks(video_id: str, chunks: list[TranscriptChunk]):
    """Stores transcript chunks in MongoDB."""
    embeddings = embed_many([chunk.text for chunk in chunks])
    docs = [{
        "source_id": video_id,
        "text": chunk.text,
        "start": chunk.start,
        "duration": chunk.duration,
        "embedding": embedding
    } for chunk, embedding in zip(chunks, embeddings)]
    store_chunks("transcript_chunks", video_id, docs)

def find_relevant_youtube_resource(task_description: str) -> dict[str, Any]:
    """Finds the most relevant YouTube video and timestamp for a given task."""

    search_result = search_youtube_video(task_description)
    if search_result.get("status") == "error":
        return dict(status="error", message=search_result.get("message"))

    for video_data in search_result.get("data", []):
        video = YouTubeVideoResult(**video_data)
        transcript_result = get_youtube_video_transcript(video.video_id)
        if transcript_result.get("status") == "error":
            continue

        store_transcript_chunks(video.video_id, [TranscriptChunk(**c) for c in transcript_result.get("data", [])])

        chunk = query_chunks(
            collection_name="transcript_chunks",
            source_id=video.video_id,
            task_description=task_description
        )
        if not chunk:
            continue

        resource = Resource(
            title=video.title,
            url=f"https://www.youtube.com/watch?v={video.video_id}&t={chunk['start']}s",
            type="youtube",
            timestamp_start=chunk["start"],
            timestamp_end=chunk["end"]
        )
        return dict(status="success", data=resource.model_dump())

    return dict(status="error", message="Could not find a usable video for this task.")



def web_search(query: str, max_results: int = 10) -> dict[str, Any]:
    """
    Performs a live web search using DuckDuckGo.
    Returns a dict with 'status' and a 'data' array of Resource objects.
    """
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                resource = Resource(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    type="article",
                    text_preview=r.get("body", "")
                )
                results.append(resource.model_dump())
            
            if not results:
                return dict(status="error", message="No results found.")

            return dict(status="success", data=results)
    except Exception as e:
        return dict(status="error", message=f"Error searching DuckDuckGo: {str(e)}")



def scrape_and_find_relevant_section(url: str, task_description: str) -> dict[str, Any]:
    """
    Scrapes a given URL to extract textual content, stores the content in chunks, and queries for a
    relevant section based on a task description.

    This function performs the following steps:
    1. Fetches the HTML content of the given URL.
    2. Parses and identifies readable paragraphs from the HTML.
    3. Embeds the paragraphs into vector representations.
    4. Stores the processed paragraphs (chunks) in a chunk store.
    5. Queries the stored chunks to find a relevant section that matches a task description.

    :param url: The URL of the webpage to scrape.
    :type url: str
    :param task_description: The task description used to query the chunk store for a relevant section.
    :type task_description: str
    :return: A dict indicating the operation's status and either the relevant
             resource or error details.
    :rtype: dict
    """

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return dict(status="error", message=f"Failed to fetch article: {response.status_code}")
    except Exception as e:
        return dict(status="error", message=f"Request failed: {str(e)}")

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    title = title.text.strip() if title else url

    paragraphs = [
        p.text.strip()
        for p in soup.find_all("p")
        if len(p.text.strip()) > 50
    ]

    if not paragraphs:
        return dict(status="error", message="No readable content found in article.")

    embeddings = embed_many(paragraphs)
    chunks = [{
        "source_id": url,
        "text": paragraph,
        "start": i,
        "duration": 1,
        "embedding": embedding
    } for i, (paragraph, embedding) in enumerate(zip(paragraphs, embeddings))]

    store_chunks("article_chunks", url, chunks)

    result = query_chunks("article_chunks", url, task_description, "article_vector_index")
    if not result:
        return dict(status="error", message="Could not find relevant section in article.")

    resource = Resource(
        title=title,
        url=url,
        type="article",
        timestamp_start=None,
        text_preview=result["text_preview"]
    )
    return dict(status="success", data=resource.model_dump())
