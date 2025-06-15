import sys
from pathlib import Path
import asyncio
from datetime import datetime
import nest_asyncio
import streamlit as st
import requests
import pandas as pd

PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.config.settings import settings
from src.agents.graph import get_workflow, get_initial_state
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
nest_asyncio.apply()  # Enable nested event loops for Streamlit

st.set_page_config(
    page_title="ReleaseBot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Bakar31/releasebot-ai',
        'Report a bug': 'https://github.com/Bakar31/releasebot-ai/issues',
        'About': 'ReleaseBot AI - Automated Release Management and Notifications'
    }
)

def get_api_url(endpoint: str) -> str:
    return f"{settings.API_BASE_URL}{endpoint}"

def fetch_releases():
    try:
        response = requests.get(get_api_url("/releases"))
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch releases. Status code: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error fetching releases: {str(e)}")
        return []

def fetch_health():
    try:
        response = requests.get(get_api_url("/health"))
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch health. Status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching health: {str(e)}")
        return None

def initialize_session_state():
    if 'agent_state' not in st.session_state:
        st.session_state.agent_state = None
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = None
    if 'workflow' not in st.session_state:
        st.session_state.workflow = get_workflow()
    if 'agent_outputs' not in st.session_state:
        st.session_state.agent_outputs = {}
    if 'agent_states' not in st.session_state:
        st.session_state.agent_states = {
            'detect_release': {},
            'analyze_changes': {},
            'generate_content': {},
            'distribute_emails': {}
        }

def add_log(message: str, level: str = "info"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    st.session_state.logs.append(log_entry)
    logger.info(f"[{level.upper()}] {message}")

def update_agent_output(step: str, output: dict):
    st.session_state.agent_outputs[step] = output

def get_step_progress(current_step: str) -> float:
    steps = ["detect_release", "analyze_changes", "generate_content", "distribute_emails"]
    if current_step not in steps:
        return 0
    return (steps.index(current_step) + 1) / len(steps) * 100

def get_agent_state_summary(state: dict) -> dict:
    """Extract a summary of the agent state for display"""
    if not state:
        return {}
    
    summary = {}
    for key, value in state.items():
        if key == 'errors' and value:
            summary[key] = value
        elif key in ['release_tag', 'manual_trigger', 'send_status', 'retry_count']:
            summary[key] = value
        elif key in ['release_data', 'analyzed_changes', 'changelog', 'email_content']:
            if value:  # Only include non-empty values
                if isinstance(value, dict):
                    summary[f"{key}_summary"] = {k: type(v).__name__ for k, v in value.items()}
                else:
                    summary[f"{key}_summary"] = f"{type(value).__name__} ({len(str(value))} chars)"
    return summary

async def process_release(release_tag: str):
    try:
        st.session_state.processing = True
        st.session_state.current_step = "Initializing"
        st.session_state.agent_outputs = {}
        st.session_state.agent_states = {agent: {} for agent in st.session_state.agent_states}
        add_log(f"Starting release processing for {release_tag}")
        
        initial_state = get_initial_state(release_tag, manual_trigger=True)
        st.session_state.agent_state = initial_state
        
        config = {"recursion_limit": 10}
        
        async for state in st.session_state.workflow.astream(initial_state, config=config):
            st.session_state.agent_state = state
            current_node = state.get('current_node', 'unknown')
            st.session_state.current_step = current_node
            
            # Update the state for the current agent
            if current_node in st.session_state.agent_states:
                st.session_state.agent_states[current_node] = get_agent_state_summary(state)
            
            if state.get('errors'):
                for error in state['errors']:
                    add_log(f"Error in {current_node}: {error}", "error")
            else:
                add_log(f"Completed {current_node} step")
                update_agent_output(current_node, state)
                
            if current_node == "distribute_emails":
                if state.get('send_status') == 'completed':
                    add_log(f"Successfully sent {state.get('email_count', 0)} emails")
                elif state.get('send_status') == 'failed':
                    add_log("Email distribution failed", "error")
            
            await asyncio.sleep(0.1)
            
    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        add_log(error_msg, "error")
        logger.exception(error_msg)
    finally:
        st.session_state.processing = False
        st.session_state.current_step = None

def trigger_release(release_tag: str):
    if not st.session_state.processing:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(process_release(release_tag))
        return True
    return False

def clear_agent_states():
    """Clear all agent states and reset the workflow"""
    st.session_state.agent_states = {
        'detect_release': {},
        'analyze_changes': {},
        'generate_content': {},
        'distribute_emails': {}
    }
    st.session_state.agent_outputs = {}
    st.session_state.current_step = None
    st.session_state.agent_state = None
    st.success("Agent states cleared successfully!")

def display_agent_state(agent_name: str, state: dict):
    """Display the state of a single agent in an expandable section"""
    with st.expander(f"🔍 {agent_name.replace('_', ' ').title()} State"):
        if not state:
            st.info("No state information available")
            return
            
        cols = st.columns(2)
        for i, (key, value) in enumerate(state.items()):
            with cols[i % 2]:
                if key == 'errors' and value:
                    with st.container(border=True):
                        st.error("Errors")
                        for error in value:
                            st.error(f"❌ {error}")
                else:
                    st.json({key: value}, expanded=False)

def display_agent_output(step: str, output: dict):
    st.subheader(f"📊 {step.replace('_', ' ').title()} Output")
    
    if step == "detect_release":
        if "release_data" in output:
            st.json(output["release_data"])
    
    elif step == "analyze_changes":
        if "analyzed_changes" in output:
            st.json(output["analyzed_changes"])
        if "changelog" in output:
            st.text_area("Changelog", output["changelog"], height=200)
    
    elif step == "generate_content":
        if "email_subject" in output:
            st.text_input("Email Subject", output["email_subject"])
        if "email_content" in output:
            st.text_area("Email Content", output["email_content"], height=300)
    
    elif step == "distribute_emails":
        if "user_list" in output:
            st.dataframe(pd.DataFrame(output["user_list"]))
        if "send_status" in output:
            st.info(f"Send Status: {output['send_status']}")

initialize_session_state()

st.title("🤖 ReleaseBot AI")
st.subheader("Release Management Dashboard", divider=True)

# Add a button to clear agent states
if st.sidebar.button("🔄 Clear All Agent States", use_container_width=True):
    clear_agent_states()

# Display current agent states
st.sidebar.subheader("Agent States")
# for agent_name, state in st.session_state.get('agent_states', {}).items():
#     display_agent_state(agent_name, state)

try:
    col1, col2, col3 = st.columns(3)

    with col1:
        health_status = fetch_health()
        st.metric(
            "Repository Status",
            "Connected" if health_status else "Disconnected",
            delta=None
        )

    with col2:
        releases = fetch_releases()
        if releases:
            last_release = releases[0]
            st.metric(
                "Last Release",
                last_release["release_tag"],
                f"Processed {last_release['email_count']} emails"
            )
        else:
            st.metric("Last Release", "No releases found", None)

    st.markdown("---")

    st.subheader("Quick Actions")
    with st.form("trigger_release_form"):
        release_tag = st.text_input("Release Tag to Process")
        submitted = st.form_submit_button(
            "Trigger Release Processing",
            disabled=st.session_state.processing
        )
        
        if submitted and release_tag:
            if trigger_release(release_tag):
                st.success(f"Release {release_tag} processing started!")
            else:
                st.error("Release processing already in progress")

    st.markdown("---")

    if st.session_state.processing or st.session_state.agent_outputs:
        st.subheader("Processing Status")
        
        progress_col1, progress_col2 = st.columns([1, 2])
        
        with progress_col1:
            st.metric("Current Step", st.session_state.current_step or "Completed")
        
        with progress_col2:
            progress = get_step_progress(st.session_state.current_step)
            st.progress(progress)
            
        st.subheader("Agent Outputs")
        for step, output in st.session_state.agent_outputs.items():
            display_agent_output(step, output)
            
        st.subheader("Processing Logs")
        log_container = st.container()
        with log_container:
            for log in st.session_state.logs[-10:]:
                if log["level"] == "error":
                    st.error(f"{log['timestamp']} - {log['message']}")
                else:
                    st.info(f"{log['timestamp']} - {log['message']}")

    st.markdown("---")

    st.subheader("Recent Activity")
    if releases:
        df = pd.DataFrame(releases)
        df["processed_at"] = pd.to_datetime(df["processed_at"])
        df = df.sort_values("processed_at", ascending=False)
        
        st.dataframe(
            df[["release_tag", "status", "processed_at", "email_count"]],
            hide_index=True
        )
    else:
        st.info("No recent activity to display")

    st.markdown("---")

    st.subheader("System Health")
    health = fetch_health()
    if health:
        st.json(health)
    else:
        st.error("Unable to fetch system health status")

except Exception as e:
    logger.error(f"Error in main app: {str(e)}")
    st.error(f"An error occurred: {str(e)}") 