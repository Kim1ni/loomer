import argparse
import asyncio
import json
import sys
from typing import AsyncGenerator

import httpx

RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"


async def parse_sse(response: httpx.Response) -> AsyncGenerator[tuple[str, dict], None]:
    event = "message"
    data_lines: list[str] = []

    async for line in response.aiter_lines():
        if line == "":
            if data_lines:
                payload = "\n".join(data_lines)
                try:
                    yield event, json.loads(payload)
                except json.JSONDecodeError:
                    yield event, {"raw": payload}
            event = "message"
            data_lines = []
            continue

        if line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            data_lines.append(line[5:].lstrip())


def render(event: str, data: dict, state: dict) -> None:
    if event == "session":
        print(f"{DIM}[session {data['session_id']}]{RESET}")

    elif event == "text":
        author = data.get("author", "agent")
        text = data.get("text", "")
        partial = data.get("partial", False)

        if state.get("streaming_author") != author:
            if state.get("streaming_author") is not None:
                print()
            print(f"{BOLD}{CYAN}{author}:{RESET} ", end="", flush=True)
            state["streaming_author"] = author

        print(text, end="" if partial else "\n", flush=True)
        if not partial:
            state["streaming_author"] = None

    elif event == "tool_call":
        if state.get("streaming_author") is not None:
            print()
            state["streaming_author"] = None
        name = data.get("name", "?")
        args = data.get("args", {})
        args_str = ", ".join(f"{k}={v!r}" for k, v in args.items())
        print(f"{YELLOW}→ tool_call{RESET} {BOLD}{name}{RESET}({args_str})")

    elif event == "tool_result":
        name = data.get("name", "?")
        resp = data.get("response", {})
        resp_str = json.dumps(resp, ensure_ascii=False)
        if len(resp_str) > 200:
            resp_str = resp_str[:197] + "..."
        print(f"{GREEN}← tool_result{RESET} {BOLD}{name}{RESET} {DIM}{resp_str}{RESET}")

    # RENDERING FOR OUR NEW PROJECT_CREATED EVENT
    elif event == "project_created":
        if state.get("streaming_author") is not None:
            print()
            state["streaming_author"] = None
        project_id = data.get("projectId", "?")
        print(f"{BOLD}{MAGENTA}★ project_created{RESET} {DIM}ID: {project_id}{RESET}")

    elif event == "error":
        if state.get("streaming_author") is not None:
            print()
            state["streaming_author"] = None
        print(f"{RED}! error{RESET} [{data.get('author', '?')}] {data.get('message', '')}")

    elif event == "done":
        if state.get("streaming_author") is not None:
            print()
            state["streaming_author"] = None
        print(f"{DIM}[done]{RESET}")

    else:
        print(f"{MAGENTA}? {event}{RESET} {data}")


async def send(url: str, message: str, session_id: str | None, user_id: str) -> str | None:
    body = {"message": message, "user_id": user_id}
    if session_id:
        body["session_id"] = session_id

    state: dict = {"streaming_author": None}
    new_session_id = session_id

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=body) as response:
            response.raise_for_status()
            async for event, data in parse_sse(response):
                if event == "session":
                    new_session_id = data.get("session_id")
                render(event, data, state)

    return new_session_id


async def chat_loop(url: str, user_id: str) -> None:
    print(f"{BLUE}Connected to {url}. Type 'exit' to quit.{RESET}\n")
    session_id: str | None = None
    while True:
        try:
            message = input(f"{BOLD}you:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not message:
            continue
        if message.lower() in {"exit", "quit"}:
            return
        try:
            session_id = await send(url, message, session_id, user_id)
        except httpx.HTTPError as e:
            print(f"{RED}HTTP error: {e}{RESET}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream events from the loomer agent.")
    parser.add_argument("--url", default="http://127.0.0.1:8000/loom/chat/stream")
    parser.add_argument("--user", default="default-user")
    parser.add_argument("-m", "--message", help="Send one message and exit (non-interactive).")
    args = parser.parse_args()

    if args.message:
        asyncio.run(send(args.url, args.message, None, args.user))
    else:
        asyncio.run(chat_loop(args.url, args.user))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
