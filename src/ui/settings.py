import streamlit as st
import requests
import json
from src.config.settings import settings

def get_api_url(endpoint: str) -> str:
    return f"{settings.API_BASE_URL}{endpoint}"

def fetch_settings():
    response = requests.get(get_api_url("/settings"))
    return response.json() if response.status_code == 200 else None

def update_settings(settings_data: dict):
    response = requests.put(
        get_api_url("/settings"),
        json=settings_data
    )
    return response.json() if response.status_code == 200 else None

def test_github_connection(token: str, repo: str):
    response = requests.post(
        get_api_url("/settings/test-github"),
        json={"token": token, "repo": repo}
    )
    return response.json() if response.status_code == 200 else None

def test_brevo_connection(api_key: str):
    response = requests.post(
        get_api_url("/settings/test-brevo"),
        json={"api_key": api_key}
    )
    return response.json() if response.status_code == 200 else None

st.set_page_config(
    page_title="Settings - ReleaseBot AI",
    page_icon="⚙️",
    layout="wide"
)

st.title("System Configuration")

settings_data = fetch_settings()

if not settings_data:
    st.error("Unable to fetch current settings")
    st.stop()

tab1, tab2, tab3 = st.tabs(["API Configuration", "Email Templates", "Workflow Settings"])

with tab1:
    st.subheader("GitHub Configuration")
    
    with st.form("github_settings"):
        github_token = st.text_input(
            "GitHub Token",
            value=settings_data.get("github_token", ""),
            type="password"
        )
        github_repo = st.text_input(
            "Repository",
            value=settings_data.get("github_repo", "")
        )
        
        col1, col2 = st.columns(2)
        with col1:
            test_github = st.form_submit_button("Test Connection")
        with col2:
            save_github = st.form_submit_button("Save GitHub Settings")
            
        if test_github:
            with st.spinner("Testing GitHub connection..."):
                result = test_github_connection(github_token, github_repo)
                if result and result.get("success"):
                    st.success("GitHub connection successful!")
                else:
                    st.error("GitHub connection failed")
                    
        if save_github:
            with st.spinner("Saving GitHub settings..."):
                settings_data["github_token"] = github_token
                settings_data["github_repo"] = github_repo
                result = update_settings(settings_data)
                if result:
                    st.success("GitHub settings saved!")
                else:
                    st.error("Failed to save GitHub settings")
    
    st.markdown("---")
    
    st.subheader("Brevo Configuration")
    
    with st.form("brevo_settings"):
        brevo_key = st.text_input(
            "Brevo API Key",
            value=settings_data.get("brevo_api_key", ""),
            type="password"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            test_brevo = st.form_submit_button("Test Connection")
        with col2:
            save_brevo = st.form_submit_button("Save Brevo Settings")
            
        if test_brevo:
            with st.spinner("Testing Brevo connection..."):
                result = test_brevo_connection(brevo_key)
                if result and result.get("success"):
                    st.success("Brevo connection successful!")
                else:
                    st.error("Brevo connection failed")
                    
        if save_brevo:
            with st.spinner("Saving Brevo settings..."):
                settings_data["brevo_api_key"] = brevo_key
                result = update_settings(settings_data)
                if result:
                    st.success("Brevo settings saved!")
                else:
                    st.error("Failed to save Brevo settings")

with tab2:
    st.subheader("Email Template Configuration")
    
    with st.form("email_template"):
        subject_template = st.text_area(
            "Subject Template",
            value=settings_data.get("email_subject_template", ""),
            height=100
        )
        content_template = st.text_area(
            "Content Template",
            value=settings_data.get("email_content_template", ""),
            height=400
        )
        
        if st.form_submit_button("Save Templates"):
            with st.spinner("Saving email templates..."):
                settings_data["email_subject_template"] = subject_template
                settings_data["email_content_template"] = content_template
                result = update_settings(settings_data)
                if result:
                    st.success("Email templates saved!")
                else:
                    st.error("Failed to save email templates")

with tab3:
    st.subheader("Workflow Configuration")
    
    with st.form("workflow_settings"):
        quality_threshold = st.slider(
            "Quality Check Threshold",
            min_value=1.0,
            max_value=10.0,
            value=float(settings_data.get("quality_threshold", 7.0)),
            step=0.5
        )
        
        max_retries = st.number_input(
            "Maximum Retries",
            min_value=1,
            max_value=5,
            value=int(settings_data.get("max_retries", 3))
        )
        
        batch_size = st.number_input(
            "Email Batch Size",
            min_value=10,
            max_value=100,
            value=int(settings_data.get("batch_size", 50))
        )
        
        if st.form_submit_button("Save Workflow Settings"):
            with st.spinner("Saving workflow settings..."):
                settings_data["quality_threshold"] = quality_threshold
                settings_data["max_retries"] = max_retries
                settings_data["batch_size"] = batch_size
                result = update_settings(settings_data)
                if result:
                    st.success("Workflow settings saved!")
                else:
                    st.error("Failed to save workflow settings") 