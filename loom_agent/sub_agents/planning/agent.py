from google.adk.agents import LlmAgent

from shared.consts import AGENT_MODEL
from sub_agents.planning import prompt
from tools.phase_tools import set_current_phase_index, get_current_phase_index, save_phases, is_phase_complete
from tools.preference_tools import get_user_goal, get_domain, get_experience_level
from tools.project_tools import set_project_id, get_current_project_state
from tools.task_tools import set_current_task_index, save_tasks

planning_agent = LlmAgent(
    name="PlanningAgent",
    model=AGENT_MODEL,
    description="Generates phases and tasks for the user's project.",
    instruction=prompt.PLANNING_AGENT_PROMPT,
    tools=[
        get_user_goal, get_domain, get_experience_level,
        get_current_phase_index, set_current_phase_index,
        set_current_task_index, set_project_id,
        save_phases, save_tasks,
        get_current_project_state, is_phase_complete
    ]
)