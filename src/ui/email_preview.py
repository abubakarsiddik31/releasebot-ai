import streamlit as st
import requests
from datetime import datetime
import pandas as pd
from src.config.settings import settings

def get_api_url(endpoint: str) -> str:
    return f"{settings.API_BASE_URL}{endpoint}"

def fetch_campaigns():
    response = requests.get(get_api_url("/campaigns"))
    return response.json() if response.status_code == 200 else []

def fetch_campaign_details(campaign_id: int):
    response = requests.get(get_api_url(f"/campaigns/{campaign_id}"))
    return response.json() if response.status_code == 200 else None

def send_campaign(campaign_id: int):
    response = requests.post(get_api_url(f"/campaigns/{campaign_id}/send"))
    return response.json() if response.status_code == 200 else None

st.set_page_config(
    page_title="Email Preview - ReleaseBot AI",
    page_icon="📧",
    layout="wide"
)

st.title("Email Preview and Management")

campaigns = fetch_campaigns()

if not campaigns:
    st.info("No campaigns available")
    st.stop()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Campaigns")
    
    selected_campaign = st.selectbox(
        "Select Campaign",
        options=campaigns,
        format_func=lambda x: f"{x['release_tag']} - {x['subject']}"
    )
    
    if selected_campaign:
        st.markdown("---")
        st.subheader("Campaign Details")
        st.write(f"Release Tag: {selected_campaign['release_tag']}")
        st.write(f"Generated: {selected_campaign['generated_at']}")
        
        if st.button("Send Campaign"):
            with st.spinner("Sending campaign..."):
                result = send_campaign(selected_campaign['id'])
                if result:
                    st.success("Campaign sent successfully!")
                else:
                    st.error("Failed to send campaign")

with col2:
    if selected_campaign:
        st.subheader("Email Preview")
        
        details = fetch_campaign_details(selected_campaign['id'])
        if details:
            st.markdown("### Subject")
            st.write(details['subject'])
            
            st.markdown("### Content")
            st.components.v1.html(
                details['content'],
                height=600,
                scrolling=True
            )
        else:
            st.error("Unable to fetch campaign details")

st.markdown("---")

st.subheader("Campaign History")
if campaigns:
    df = pd.DataFrame(campaigns)
    df["generated_at"] = pd.to_datetime(df["generated_at"])
    df = df.sort_values("generated_at", ascending=False)
    
    st.dataframe(
        df[["release_tag", "subject", "generated_at"]],
        hide_index=True
    ) 