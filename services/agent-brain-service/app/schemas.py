from typing import TypedDict, Dict, List, Optional


class AgentState(TypedDict, total=False):
    """
    State schema for the LangGraph agent.
    Using TypedDict instead of BaseModel for LangGraph compatibility.
    """
    anomaly: Dict
    hypotheses: Optional[List[str]]
    policy_flags: Optional[Dict]
    proposed_action: Optional[str]
    explanation: Optional[str]