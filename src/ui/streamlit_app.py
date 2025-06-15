import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.append(project_root)

import streamlit as st
import requests
import pandas as pd
from src.config.settings import settings

st.set_page_config(
    page_title="ReleaseBot AI Dashboard",
    page_icon="🤖",
    layout="wide"
)

def get_api_url(endpoint: str) -> str:
    return f"{settings.API_BASE_URL}{endpoint}"

def fetch_releases():
    response = requests.get(get_api_url("/releases"))
    return response.json() if response.status_code == 200 else []

def fetch_health():
    response = requests.get(get_api_url("/health"))
    return response.json() if response.status_code == 200 else None

def trigger_release(release_tag: str):
    response = requests.post(
        get_api_url("/trigger-release"),
        json={"release_tag": release_tag}
    )
    return response.json() if response.status_code == 200 else None

st.title("ReleaseBot AI Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Repository Status",
        "Connected" if fetch_health() else "Disconnected",
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

with col3:
    if releases:
        success_rate = sum(1 for r in releases if r["status"] == "completed") / len(releases) * 100
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            f"Based on {len(releases)} releases"
        )

st.markdown("---")

st.subheader("Quick Actions")
with st.form("trigger_release_form"):
    release_tag = st.text_input("Release Tag to Process")
    submitted = st.form_submit_button("Trigger Release Processing")
    
    if submitted and release_tag:
        with st.spinner("Triggering release processing..."):
            result = trigger_release(release_tag)
            if result:
                st.success(f"Release {release_tag} processing started!")
            else:
                st.error("Failed to trigger release processing")

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