import streamlit as st
import requests
import pandas as pd
from src.config.settings import settings

def get_api_url(endpoint: str) -> str:
    return f"{settings.API_BASE_URL}{endpoint}"

def fetch_users():
    response = requests.get(get_api_url("/users"))
    return response.json() if response.status_code == 200 else []

def create_user(email: str, name: str):
    response = requests.post(
        get_api_url("/users"),
        json={"email": email, "name": name}
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

st.title("User Management")

tab1, tab2 = st.tabs(["User List", "Add Users"])

with tab1:
    st.subheader("Registered Users")
    
    users = fetch_users()
    
    if users:
        users_df = pd.DataFrame(users)
        st.dataframe(
            users_df,
            column_config={
                "email": "Email",
                "name": "Name",
                "created_at": "Created At"
            },
            use_container_width=True
        )
    else:
        st.info("No users found")

with tab2:
    st.subheader("Add Single User")
    
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email")
    with col2:
        name = st.text_input("Name")
        
    if st.button("Add User"):
        if email and name:
            if create_user(email, name):
                st.success(f"Added user: {email}")
                st.rerun()
            else:
                st.error("Failed to add user")
        else:
            st.warning("Please fill in all fields")
    
    st.divider()
    
    st.subheader("Bulk Import Users")
    st.markdown("Upload a CSV file with columns: `email`, `name`")
    
    uploaded_file = st.file_uploader("Choose CSV file", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'email' in df.columns and 'name' in df.columns:
            if st.button("Import Users"):
                success, failed = process_bulk_import(df)
                
                st.write("Import Results:")
                st.success(f"Successfully added {len(success)} users")
                if failed:
                    st.error(f"Failed to add {len(failed)} users")
                    st.write("Failed emails:", ", ".join(failed))
                
                st.rerun()
        else:
            st.error("CSV file must contain 'email' and 'name' columns")
