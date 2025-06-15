from typing import Dict, Any, TypedDict, List, Callable, Awaitable, Optional, Literal, Union, Sequence, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain.tools import BaseTool
from typing_extensions import TypedDict

from src.agents.release_detector import ReleaseDetector
from src.agents.change_analyzer import ChangeAnalyzer
from src.agents.content_generator import ContentGenerator
from src.agents.quality_checker import QualityChecker
from src.agents.email_distributor import EmailDistributor
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AgentState(TypedDict):
    # State that should only be set once
    release_tag: str
    manual_trigger: bool
    
    # State that can be updated by nodes
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
    errors: Annotated[List[str], operator.add]  # Using operator.add as reducer
    retry_count: int
    revision_count: int

def get_workflow() -> StateGraph:
    graph = StateGraph(AgentState)
    
    # Create tool instances
    release_detector = ReleaseDetector()
    change_analyzer = ChangeAnalyzer()
    content_generator = ContentGenerator()
    quality_checker = QualityChecker()
    email_distributor = EmailDistributor()

    def should_retry(state: Dict[str, Any]) -> bool:
        max_retries = 3
        max_revisions = 5
        
        revision_count = state.get('revision_count', 0)
        retry_count = state.get('retry_count', 0)
        
        has_errors = bool(state.get('errors'))
        needs_revision = state.get('needs_revision', False)
        
        if has_errors and retry_count < max_retries:
            return True
            
        if needs_revision and revision_count < max_revisions:
            return True
            
        return False

    def handle_errors(state: Dict[str, Any]) -> Dict[str, Any]:
        current_errors = state.get('errors', [])
        if current_errors:
            logger.error("Workflow errors: %s", current_errors)
        
        return {
            'retry_count': state.get('retry_count', 0) + 1,
            'errors': []
        }

    def check_quality_threshold(state: Dict[str, Any]) -> str:
        if state.get('approved', False):
            return "approved"
            
        revision_count = state.get('revision_count', 0) + 1
        
        if revision_count >= 5:
            logger.warning("Maximum revisions (%d) reached. Proceeding with current content.", revision_count)
            return "approved"
            
        return "needs_revision"

    def check_send_status(state: Dict[str, Any]) -> str:
        if state.get('send_status') == 'completed':
            return "completed"
        if state.get('send_status') == 'failed':
            return "failed"
        return "processing"

    def create_tool_node(tool: BaseTool) -> Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]:
        async def tool_node(state: Dict[str, Any]) -> Dict[str, Any]:
            tool_name = tool.name if hasattr(tool, 'name') else tool.__class__.__name__
            logger.info(f"🚀 Starting {tool_name} with state: {_get_sanitized_state(state)}")
            
            try:
                result = await tool._arun(state.copy())
                
                if not isinstance(result, dict):
                    raise ValueError(f"Tool {tool_name} did not return a dictionary")
                
                updates = {}
                
                for key, value in result.items():
                    if key in {'release_tag', 'manual_trigger'}:
                        logger.warning("Attempted to modify immutable field: %s", key)
                        continue
                        
                    if key in state and state[key] != value:
                        updates[key] = value
                
                logger.info(f"✅ {tool_name} completed. Updates: {_get_sanitized_updates(updates)}")
                logger.debug(f"Full state after {tool_name}: {_get_sanitized_state({**state, **updates})}")
                return updates
                
            except Exception as e:
                error_msg = f"❌ Error in {tool_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {'errors': [error_msg]}
        
        def _get_sanitized_state(state: Dict[str, Any]) -> Dict[str, Any]:
            """Create a sanitized version of the state for logging."""
            if not state:
                return {}
                
            sanitized = state.copy()
            # Remove large fields from logging
            for field in ['email_content', 'changelog', 'release_data', 'analyzed_changes']:
                if field in sanitized and sanitized[field]:
                    sanitized[field] = f"<{field} - {len(str(sanitized[field]))} chars>"
            return sanitized
            
        def _get_sanitized_updates(updates: Dict[str, Any]) -> Dict[str, Any]:
            """Create a sanitized version of updates for logging."""
            if not updates:
                return {}
                
            sanitized = updates.copy()
            for field in ['email_content', 'changelog', 'release_data', 'analyzed_changes']:
                if field in sanitized and sanitized[field]:
                    sanitized[field] = f"<{field} updated - {len(str(sanitized[field]))} chars>"
            return sanitized
                
        return tool_node

    graph.add_node("detect_release", create_tool_node(release_detector))
    graph.add_node("analyze_changes", create_tool_node(change_analyzer))
    graph.add_node("generate_content", create_tool_node(content_generator))
    graph.add_node("check_quality", create_tool_node(quality_checker))
    graph.add_node("distribute_emails", create_tool_node(email_distributor))
    graph.add_node("handle_errors", handle_errors)

    def after_detect_release(state: Dict[str, Any]) -> str:
        if state.get('errors'):
            return "handle_errors"
        return "analyze_changes"
    
    def after_analyze_changes(state: Dict[str, Any]) -> str:
        if state.get('errors'):
            return "handle_errors"
        return "generate_content"
    
    def after_generate_content(state: Dict[str, Any]) -> str:
        if state.get('errors'):
            return "handle_errors"
        return "check_quality"
    
    def after_handle_errors(state: Dict[str, Any]) -> str:
        if should_retry(state):
            if state.get('revision_count', 0) > 0:
                return "generate_content"
            return "detect_release"
        return END
    
    graph.add_edge("detect_release", "analyze_changes")
    graph.add_conditional_edges("detect_release", after_detect_release)
    
    graph.add_edge("analyze_changes", "generate_content")
    graph.add_conditional_edges("analyze_changes", after_analyze_changes)
    
    graph.add_edge("generate_content", "check_quality")
    graph.add_conditional_edges("generate_content", after_generate_content)
    
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
        after_handle_errors
    )

    graph.set_entry_point("detect_release")
    
    return graph.compile()

def get_initial_state(release_tag: str, manual_trigger: bool = False) -> Dict[str, Any]:
    """Initialize the workflow state with all required fields.
    
    Args:
        release_tag: The release tag to process
        manual_trigger: Whether this is a manual trigger
        
    Returns:
        Dict containing the initial state with all required fields
    """
    return {
        # Immutable fields (set once at start)
        "release_tag": release_tag,
        "manual_trigger": manual_trigger,
        
        # Mutable fields (can be updated by nodes)
        "release_data": {},
        "changelog": "",
        "analyzed_changes": {},
        "feature_summary": "",
        "email_subject": "",
        "email_content": "",
        "quality_score": 0.0,
        "quality_feedback": "",
        "approved": False,
        "user_list": [],
        "send_status": "pending",
        "errors": [],
        
        # Control fields
        "retry_count": 0,
        "revision_count": 0
    }