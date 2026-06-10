from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

import prompt
from loom_agent.sub_agents.onboarding.agent import onboarding_agent
from loom_agent.sub_agents.planning.agent import planning_agent
from loom_agent.sub_agents.progress.agent import progress_agent
from loom_agent.sub_agents.resource.agent import resource_agent
from shared.consts import MONGODB_URI, AGENT_MODEL
from tools.project_tools import (
    save_project, load_project, list_projects, get_project_id,
    get_current_project_state, get_progress_summary
)
#
# mongodb_mcp_toolset = McpToolset(
#     connection_params=StdioConnectionParams(
#         server_params=StdioServerParameters(
#             command="npx",
#             args=[
#                 "-y",
#                 "mongodb-mcp-server"
#             ],
#             env={
#                 "MDB_MCP_CONNECTION_STRING" : MONGODB_URI
#             }
#         ),
#         timeout=30
#     )
# )

root_agent = LlmAgent(
    name="LoomAgent",
    model=AGENT_MODEL,
    description="Loom — an AI learning companion that guides users through any project.",
    instruction=prompt.LOOM_AGENT_PROMPT,
    tools=[
        get_project_id,
        get_current_project_state,
        get_progress_summary,
        save_project,
        load_project,
        list_projects,
        # mongodb_mcp_toolset,
    ],
    sub_agents=[
        onboarding_agent,
        planning_agent,
        resource_agent,
        progress_agent,
    ]
)
