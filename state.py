from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    user_query: str
    messages: List[BaseMessage]           # Centralized memory
    parsed_input: Optional[Dict[str, Any]]
    plan: Dict[str, Any]
    current_step: Optional[Dict]
    results: Dict[str, Any]
    final_report: Optional[str]
    should_continue: str  # "continue" or "end"
    step_index: Optional[int]