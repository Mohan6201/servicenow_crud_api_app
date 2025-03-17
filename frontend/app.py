import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="ServiceNow Incident Manager", layout="wide")
st.markdown("""
    <style>
        body { background-color: #1E1E1E; color: white; }
        .main { background-color: #1E1E1E; color: white; }
        .stApp { max-width: 1200px; margin: auto; }
        .sidebar { background-color: #333333; color: white; }
        .stButton>button { width: 100%; padding: 10px; background-color: #0078D7; color: white; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Create Incident", "Retrieve Incident(s)", "Update Incident", "Delete Incident", "Fetch All Incidents"])

def display_incidents(data):
    if data:
        df = pd.DataFrame(data)
        columns_order = [
            "sys_id", "number", "opened_at", "short_description", "caller_id",
            "priority", "state", "category", "assignment_group", "assigned_to",
            "sys_updated_on", "sys_updated_by"
        ]
        df = df[columns_order]
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No incidents found.")

if page == "Fetch All Incidents":
    st.title("📋 All Incidents")
    if st.button("Fetch Incidents"):
        response = requests.get(f"{BASE_URL}/incidents")
        if response.status_code == 200:
            display_incidents(response.json().get("result", []))
        else:
            st.error("Failed to fetch incidents")

elif page == "Retrieve Incident(s)":
    st.title("🔍 Retrieve Incident(s)")
    sys_ids = st.text_input("Enter sys_id(s) (comma-separated)", "")
    if st.button("Retrieve"):
        if sys_ids:
            response = requests.get(f"{BASE_URL}/incidents/{sys_ids}")
            if response.status_code == 200:
                display_incidents(response.json().get("result", []))
            else:
                st.error("Failed to retrieve incident(s)")

elif page == "Create Incident":
    st.title("📝 Create a New Incident")
    short_desc = st.text_input("Short Description")
    caller_id = st.text_input("Caller ID")
    priority = st.selectbox("Priority", [1, 2, 3, 4, 5])
    state = st.selectbox("State", ["New", "In Progress", "Resolved", "Closed"])
    category = st.selectbox("Category", ["Inquiry / Help", "Database", "Network", "Hardware", "Software"])
    assignment_group = st.selectbox("Assignment Group", ["Service Desk", "Openspace", "Network", "Hardware", "Software"])
    assigned_to = st.text_input("Assigned To")

    if st.button("Create Incident"):
        if short_desc and caller_id:
            data = {
                "short_description": short_desc,
                "caller_id": caller_id,
                "priority": priority,
                "state": state,
                "category": category,
                "assignment_group": assignment_group,
                "assigned_to": assigned_to
            }
            response = requests.post(f"{BASE_URL}/incidents", json=data)
            if response.status_code == 201:
                st.success("Incident created successfully")
            else:
                st.error("Failed to create incident")
        else:
            st.warning("Please fill in all required fields.")

elif page == "Update Incident":
    st.title("🔄 Update an Incident")
    update_sys_id = st.text_input("Enter sys_id to Update")
    update_field = st.selectbox("Select Field to Update", ["short_description", "priority", "state", "category", "assignment_group", "assigned_to"])
    update_value = st.text_input(f"New {update_field} Value")

    if st.button("Update"):
        if update_sys_id:
            response = requests.put(f"{BASE_URL}/incidents/{update_sys_id}", json={update_field: update_value})
            if response.status_code == 200:
                st.success(f"Incident {update_sys_id} updated successfully")
            else:
                st.error("Failed to update incident")

elif page == "Delete Incident":
    st.title("🗑 Delete an Incident")
    delete_sys_id = st.text_input("Enter sys_id to Delete")
    if st.button("Delete"):
        if delete_sys_id:
            response = requests.delete(f"{BASE_URL}/incidents/{delete_sys_id}")
            if response.status_code == 200:
                st.success(f"Incident {delete_sys_id} deleted successfully")
            else:
                st.error("Failed to delete incident")

st.write("Made with ❤️ for ServiceNow Integration")
