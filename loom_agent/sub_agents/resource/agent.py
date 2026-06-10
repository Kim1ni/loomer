from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

from duckduckgo_search import DDGS

from shared.consts import AGENT_MODEL
from sub_agents.resource import prompt

from tools.preference_tools import get_preferred_resource_types
from tools.project_tools import get_current_project_state
from tools.resource_tools import (
    scrape_and_find_relevant_section,
    find_relevant_youtube_resource,
    web_search
)
from tools.task_tools import get_current_task_index, update_task_with_resources

# duckduckgo_mcp_server = McpToolset(
#     connection_params=StdioConnectionParams(
#         server_params=StdioServerParameters(
#             command="npx",
#             args=[
#                 "-y",
#                 "duckduckgo-mcp-server"
#             ]
#         ),
#         timeout=30
#     )
# )

resource_agent = LlmAgent(
    name="ResourceAgent",
    model=AGENT_MODEL,
    description="Finds and presents resources for the current task.",
    instruction=prompt.RESOURCE_AGENT_PROMPT,
    tools=[
        get_current_task_index,
        get_preferred_resource_types,
        update_task_with_resources,
        get_current_project_state,
        find_relevant_youtube_resource,
        scrape_and_find_relevant_section,
        web_search
    ]
)
