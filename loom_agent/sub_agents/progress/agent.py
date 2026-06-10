from google.adk.agents import LlmAgent

from shared.consts import AGENT_MODEL
from sub_agents.progress import prompt
from tools.phase_tools import (
    set_current_phase_index, get_current_phase_index, is_phase_complete
)
from tools.project_tools import (
    get_current_project_state, get_progress_summary
)
from tools.session_tools import (
    get_stuck_count, increment_stuck_count, log_debug_note, get_debug_notes,
    get_ideas, capture_idea
)
from tools.task_tools import (
    set_current_task_index, get_current_task_index, increment_task_index,
    save_tasks, mark_task_complete
)

progress_agent = LlmAgent(
    name="ProgressAgent",
    model=AGENT_MODEL,
    description="Tracks user progress, handles stuck users, logs debug notes, and captures ideas.",
    instruction=prompt.PROGRESS_AGENT_PROMPT,
    tools=[
        get_current_task_index, increment_task_index, get_current_phase_index,
        set_current_phase_index, set_current_task_index, save_tasks,
        get_current_project_state, is_phase_complete, mark_task_complete,
        increment_stuck_count, get_stuck_count, log_debug_note,
        get_debug_notes, capture_idea, get_ideas, get_progress_summary,
    ]
)
