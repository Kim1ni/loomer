from google.adk.agents import LlmAgent

from shared.consts import AGENT_MODEL
from sub_agents.onboarding import prompt
from tools.preference_tools import (
    set_user_name, get_user_name, set_user_goal, get_domain,
    get_user_goal, set_domain, set_experience_level, get_experience_level,
    set_preferred_resource_types, get_preferred_resource_types
)

onboarding_agent = LlmAgent(
    name="OnboardingAgent",
    model=AGENT_MODEL,
    description="Collects user information before starting a project.",
    instruction=prompt.ONBOARDING_AGENT_PROMPT,
    tools=[
        set_user_name, get_user_name,
        set_user_goal, get_user_goal,
        set_domain, get_domain,
        set_experience_level, get_experience_level,
        set_preferred_resource_types, get_preferred_resource_types,
    ]
)