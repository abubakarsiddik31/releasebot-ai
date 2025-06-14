import streamlit as st
import requests
import pandas as pd
from src.config.settings import settings

def get_api_url(endpoint: str) -> str:
    return f"{settings.API_BASE_URL}{endpoint}"

def fetch_users(status: str = None):
    url = get_api_url("/users")
    if status:
        url += f"?status={status}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def create_user(email: str, name: str):
    response = requests.post(
        get_api_url("/users"),
        json={"email": email, "name": name}
    )
    return response.json() if response.status_code == 200 else None

def update_user_status(email: str, status: str):
    response = requests.put(
        get_api_url(f"/users/{email}"),
        json={"status": status}
    )
    return response.json() if response.status_code == 200 else None

def process_bulk_import(df: pd.DataFrame):
    success = []
    failed = []
    
    for _, row in df.iterrows():
        try:
            result = create_user(row['email'], row['name'])
            if result:
                success.append(row['email'])
            else:
                failed.append(row['email'])
        except Exception:
            failed.append(row['email'])
            
    return success, failed

st.set_page_config(
    page_title="User Management - ReleaseBot AI",
    page_icon="👥",
    layout="wide"
)

st.title("User Management")

tab1, tab2 = st.tabs(["Add Users", "Manage Users"])

with tab1:
    st.subheader("Add Single User")
    with st.form("add_user_form"):
        email = st.text_input("Email")
        name = st.text_input("Name")
        submitted = st.form_submit_button("Add User")
        
        if submitted and email and name:
            with st.spinner("Adding user..."):
                result = create_user(email, name)
                if result:
                    st.success(f"User {email} added successfully!")
                else:
                    st.error("Failed to add user")
    
    st.markdown("---")
    
    st.subheader("Bulk Import")
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ['email', 'name']
            
            if all(col in df.columns for col in required_columns):
                st.write("Preview:")
                st.dataframe(df.head())
                
                if st.button("Import Users"):
                    with st.spinner("Importing users..."):
                        success, failed = process_bulk_import(df)
                        
                        if success:
                            st.success(f"Successfully imported {len(success)} users")
                        if failed:
                            st.error(f"Failed to import {len(failed)} users")
                            st.write("Failed emails:", failed)
            else:
                st.error("CSV must contain 'email' and 'name' columns")
        except Exception as e:
            st.error(f"Error processing CSV: {str(e)}")

with tab2:
    st.subheader("User List")
    
    status_filter = st.selectbox(
        "Filter by Status",
        options=["all", "active", "inactive", "bounced", "unsubscribed"],
        index=0
    )
    
    users = fetch_users(None if status_filter == "all" else status_filter)
    
    if users:
        df = pd.DataFrame(users)
        df["created_at"] = pd.to_datetime(df["created_at"])
        
        st.dataframe(
            df[["email", "name", "status", "created_at"]],
            hide_index=True
        )
        
        st.markdown("---")
        st.subheader("Bulk Actions")
        
        selected_status = st.selectbox(
            "Change Status To",
            options=["active", "inactive", "bounced", "unsubscribed"]
        )
        
        if st.button("Apply to Selected"):
            with st.spinner("Updating user statuses..."):
                for user in users:
                    update_user_status(user['email'], selected_status)
                st.success("Status updated for all users")
    else:
        st.info("No users found") 