
from typing import TypedDict, Optional, Dict, Any, List


class AgentState(TypedDict, total=False):
    question: str
    user_id: str
    user_name: Optional[str]
    birthday: Optional[str]
    enrichment: Optional[Dict[str, Any]]
    tool_output: Optional[Dict[str, Any]]
    final_answer: Optional[str]
    next_agent: Optional[str]
    # Routing plan flags and execution tracking
    plan: Optional[Dict[str, Any]]
    completed_agents: Optional[List[str]]

