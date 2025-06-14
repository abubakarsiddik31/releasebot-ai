from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.agents.release_detector import ReleaseDetector
from src.agents.change_analyzer import ChangeAnalyzer
from src.agents.content_generator import ContentGenerator
from src.agents.quality_checker import QualityChecker
from src.agents.email_distributor import EmailDistributor

class AgentState(TypedDict):
    release_tag: str
    manual_trigger: bool
    release_data: Optional[Dict[str, Any]]
    changelog: Optional[str]
    analyzed_changes: Optional[Dict[str, Any]]
    feature_summary: Optional[str]
    email_subject: Optional[str]
    email_content: Optional[str]
    quality_score: Optional[float]
    quality_feedback: Optional[str]
    approved: bool
    user_list: Optional[List[str]]
    send_status: Optional[Dict[str, Any]]
    errors: List[str]
    retry_count: int

def should_send_emails(state: AgentState) -> str:
    if state["errors"]:
        return "abort"
    if not state["approved"]:
        if state["retry_count"] >= 3:
            return "abort"
        return "regenerate"
    return "send"

def create_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)

    release_detector = ReleaseDetector()
    change_analyzer = ChangeAnalyzer()
    content_generator = ContentGenerator()
    quality_checker = QualityChecker()
    email_distributor = EmailDistributor()

    workflow.add_node("detect_release", ToolNode(release_detector))
    workflow.add_node("analyze_changes", ToolNode(change_analyzer))
    workflow.add_node("generate_content", ToolNode(content_generator))
    workflow.add_node("quality_check", ToolNode(quality_checker))
    workflow.add_node("distribute_emails", ToolNode(email_distributor))

    workflow.add_edge("detect_release", "analyze_changes")
    workflow.add_edge("analyze_changes", "generate_content")
    workflow.add_edge("generate_content", "quality_check")

    workflow.add_conditional_edges(
        "quality_check",
        should_send_emails,
        {
            "send": "distribute_emails",
            "regenerate": "generate_content",
            "abort": END
        }
    )

    workflow.add_edge("distribute_emails", END)

    return workflow.compile() 