from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from src.agents.release_detector import ReleaseDetector
from src.agents.change_analyzer import ChangeAnalyzer
from src.agents.content_generator import ContentGenerator
from src.agents.quality_checker import QualityChecker
from src.agents.email_distributor import EmailDistributor
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AgentState(TypedDict):
    release_tag: str
    manual_trigger: bool
    release_data: Dict[str, Any]
    changelog: str
    analyzed_changes: Dict[str, Any]
    feature_summary: str
    email_subject: str
    email_content: str
    quality_score: float
    quality_feedback: str
    approved: bool
    user_list: List[Dict[str, str]]
    send_status: str
    errors: List[str]
    retry_count: int

def get_workflow() -> StateGraph:
    graph = StateGraph(AgentState)
    
    release_detector = ReleaseDetector()
    change_analyzer = ChangeAnalyzer()
    content_generator = ContentGenerator()
    quality_checker = QualityChecker()
    email_distributor = EmailDistributor()

    def should_retry(state: Dict[str, Any]) -> bool:
        return state['retry_count'] < 3 and state['errors']

    def handle_errors(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.error(f"Workflow errors: {state['errors']}")
        state['retry_count'] += 1
        return state

    def check_quality_threshold(state: Dict[str, Any]) -> str:
        if state.get('approved', False):
            return "approved"
        return "needs_revision"

    def check_send_status(state: Dict[str, Any]) -> str:
        if state.get('send_status') == 'completed':
            return "completed"
        if state.get('send_status') == 'failed':
            return "failed"
        return "processing"

    graph.add_node("detect_release", release_detector.detect_release)
    graph.add_node("analyze_changes", change_analyzer.analyze_changes)
    graph.add_node("generate_content", content_generator.generate_content)
    graph.add_node("check_quality", quality_checker.check_quality)
    graph.add_node("distribute_emails", email_distributor.distribute_emails)
    graph.add_node("handle_errors", handle_errors)

    graph.add_edge("detect_release", "analyze_changes")
    graph.add_edge("analyze_changes", "generate_content")
    graph.add_edge("generate_content", "check_quality")
    graph.add_conditional_edges(
        "check_quality",
        check_quality_threshold,
        {
            "approved": "distribute_emails",
            "needs_revision": "generate_content"
        }
    )
    graph.add_conditional_edges(
        "distribute_emails",
        check_send_status,
        {
            "completed": END,
            "failed": "handle_errors",
            "processing": "distribute_emails"
        }
    )
    graph.add_conditional_edges(
        "handle_errors",
        should_retry,
        {
            True: "detect_release",
            False: END
        }
    )

    graph.set_entry_point("detect_release")
    
    return graph.compile()

def get_initial_state(release_tag: str, manual_trigger: bool = False) -> AgentState:
    return {
        'release_tag': release_tag,
        'manual_trigger': manual_trigger,
        'release_data': {},
        'changelog': '',
        'analyzed_changes': {},
        'feature_summary': '',
        'email_subject': '',
        'email_content': '',
        'quality_score': 0.0,
        'quality_feedback': '',
        'approved': False,
        'user_list': [],
        'send_status': 'pending',
        'errors': [],
        'retry_count': 0
    } 