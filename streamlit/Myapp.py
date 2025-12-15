import streamlit as st
import pandas as pd
import os
from datetime import datetime
import hashlib
import random
import string

FILE_PATH = "attendance.csv"
PROJECTS_FILE = "projects.csv"
USERS_FILE = "users.csv"
EMPLOYEES_FILE = "employees.csv"

# Title
st.title("Employee Attendance Tracker")

# Auth Functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_userdata(username, password):
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=["username", "password"])
    else:
        df = pd.read_csv(USERS_FILE)
    
    if username in df['username'].values:
        return False
    
    new_user = pd.DataFrame([[username, make_hashes(password)]], columns=["username", "password"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)
    return True

def login_user(username, password):
    if not os.path.exists(USERS_FILE):
        return False
    df = pd.read_csv(USERS_FILE)
    hashed_pswd = make_hashes(password)
    if not df.empty:
        user = df[df['username'] == username]
        if not user.empty:
            if user.iloc[0]['password'] == hashed_pswd:
                return True
    return False

def update_password(username, new_password):
    if not os.path.exists(USERS_FILE):
        return False
    df = pd.read_csv(USERS_FILE)
    if username in df['username'].values:
        idx = df.index[df['username'] == username][0]
        df.at[idx, 'password'] = make_hashes(new_password)
        df.to_csv(USERS_FILE, index=False)
        return True
    return False

def generate_reset_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def set_reset_code(username, code):
    if not os.path.exists(USERS_FILE):
        return False
    df = pd.read_csv(USERS_FILE)
    if "reset_code" not in df.columns:
        df["reset_code"] = ""
    
    if username in df['username'].values:
        idx = df.index[df['username'] == username][0]
        df['reset_code'] = df['reset_code'].astype(object)
        df.at[idx, 'reset_code'] = str(code)
        df.to_csv(USERS_FILE, index=False)
        return True
    return False

def verify_and_reset_password(username, code, new_password):
    if not os.path.exists(USERS_FILE):
        return False
    df = pd.read_csv(USERS_FILE)
    if "reset_code" not in df.columns:
        return False
    
    if username in df['username'].values:
        user_row = df[df['username'] == username].iloc[0]
        stored_code = str(user_row['reset_code'])
        if stored_code == str(code) and stored_code != "nan" and stored_code != "":
            idx = df.index[df['username'] == username][0]
            df.at[idx, 'password'] = make_hashes(new_password)
            df.at[idx, 'reset_code'] = ""
            df.to_csv(USERS_FILE, index=False)
            return True
    return False

# Check if user exists in company database
def is_valid_employee(username):
    if not os.path.exists(EMPLOYEES_FILE):
        # Create a dummy company database for demonstration
        data = {"username": ["admin", "JohnDoe", "JaneSmith"]}
        pd.DataFrame(data).to_csv(EMPLOYEES_FILE, index=False)
    
    df = pd.read_csv(EMPLOYEES_FILE)
    if "username" in df.columns:
        return username in df["username"].values
    return False

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        remember_me = st.checkbox("Remember Me")
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Incorrect Username or Password")
    with tab2:
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            if not is_valid_employee(new_user):
                st.error("Registration failed: User not found in company database.")
            elif add_userdata(new_user, new_pass):
                st.success("Account created! Please log in.")
            else:
                st.error("Username already exists.")
    with tab3:
        st.subheader("Reset Password")
        reset_user = st.text_input("Username", key="reset_user")
        if st.button("Send Reset Code"):
            if reset_user:
                code = generate_reset_code()
                if set_reset_code(reset_user, code):
                    st.info(f"Code sent! (Simulation: {code})")
                else:
                    st.error("Username not found.")
        
        st.markdown("---")
        reset_code = st.text_input("Enter Reset Code", key="reset_code_input")
        new_reset_pass = st.text_input("New Password", type="password", key="reset_new_pass")
        if st.button("Reset Password"):
            if verify_and_reset_password(reset_user, reset_code, new_reset_pass):
                st.success("Password reset successfully! You can now login.")
            else:
                st.error("Invalid code or username.")
    st.stop()

# Dark Mode Toggle
if st.sidebar.checkbox("Dark Mode"):
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        [data-testid="stSidebar"] {
            background-color: #262730;
            color: #FAFAFA;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

employee_name = st.session_state.username

def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif 12 <= hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"

col_head, col_logout = st.columns([3, 1])
with col_head:
    st.subheader(f"{get_greeting()}, {employee_name}")
with col_logout:
    st.markdown(
        """
        <style>
        button[kind="primary"] {
            background-color: #FF4B4B !important;
            border-color: #FF4B4B !important;
            color: white !important;
        }
        button[kind="primary"]:hover {
            background-color: #FF0000 !important;
            border-color: #FF0000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Logout", type="primary"):
        st.session_state.clear()
        st.rerun()

# Profile Settings
with st.sidebar.expander("Profile Settings"):
    current_pass = st.text_input("Current Password", type="password", key="p_current")
    new_pass = st.text_input("New Password", type="password", key="p_new")
    confirm_pass = st.text_input("Confirm Password", type="password", key="p_confirm")
    if st.button("Update Password"):
        if login_user(employee_name, current_pass):
            if new_pass == confirm_pass and new_pass:
                update_password(employee_name, new_pass)
                st.success("Password updated!")
            else:
                st.error("Passwords do not match or empty.")
        else:
            st.error("Incorrect current password.")

# Admin View
if employee_name == "admin":
    st.sidebar.header("Admin Panel")
    
    if os.path.exists(USERS_FILE):
        df_users = pd.read_csv(USERS_FILE)
        st.sidebar.download_button(
            label="Export User List",
            data=df_users.to_csv(index=False).encode('utf-8'),
            file_name="users_export.csv",
            mime="text/csv"
        )

    if st.sidebar.checkbox("View All Users"):
        if os.path.exists(USERS_FILE):
            st.subheader("Registered Users & Passwords (Hashed)")
            st.dataframe(pd.read_csv(USERS_FILE))
            
    if st.sidebar.checkbox("Delete Users"):
        if os.path.exists(USERS_FILE):
            users_df = pd.read_csv(USERS_FILE)
            user_to_delete = st.sidebar.selectbox("Select User to Delete", users_df["username"].tolist())
            if st.sidebar.button("Delete Selected User"):
                if user_to_delete == "admin":
                    st.sidebar.error("Cannot delete Admin account.")
                else:
                    users_df = users_df[users_df["username"] != user_to_delete]
                    users_df.to_csv(USERS_FILE, index=False)
                    st.sidebar.success(f"User '{user_to_delete}' deleted.")
                    st.rerun()

    if st.sidebar.checkbox("Manage Employees"):
        st.subheader("Company Employee Database")
        if not os.path.exists(EMPLOYEES_FILE):
            data = {"username": ["admin", "JohnDoe", "JaneSmith"]}
            pd.DataFrame(data).to_csv(EMPLOYEES_FILE, index=False)
            
        if os.path.exists(EMPLOYEES_FILE):
            emp_df = pd.read_csv(EMPLOYEES_FILE)
            st.dataframe(emp_df)
            new_emp = st.text_input("Add New Employee Username")
            if st.button("Add Employee"):
                if new_emp and new_emp not in emp_df["username"].values:
                    new_row = pd.DataFrame([{"username": new_emp}])
                    pd.concat([emp_df, new_row], ignore_index=True).to_csv(EMPLOYEES_FILE, index=False)
                    st.success(f"Added {new_emp}")
                    st.rerun()
                elif new_emp:
                    st.warning("Employee already exists.")
            
            st.markdown("---")
            emp_to_remove = st.selectbox("Remove Employee", emp_df["username"].tolist(), key="remove_emp_select")
            if st.button("Remove Employee"):
                if emp_to_remove == "admin":
                    st.error("Cannot remove Admin.")
                else:
                    emp_df = emp_df[emp_df["username"] != emp_to_remove]
                    emp_df.to_csv(EMPLOYEES_FILE, index=False)
                    
                    msg = f"Removed '{emp_to_remove}' from database."
                    if os.path.exists(USERS_FILE):
                        users_df = pd.read_csv(USERS_FILE)
                        if emp_to_remove in users_df["username"].values:
                            users_df = users_df[users_df["username"] != emp_to_remove]
                            users_df.to_csv(USERS_FILE, index=False)
                            msg += " Access revoked."
                    st.success(msg)
                    st.rerun()

# Load or initialize projects
if os.path.exists(PROJECTS_FILE):
    project_options = pd.read_csv(PROJECTS_FILE)["Project"].tolist()
else:
    project_options = ["Ceiling Project", "Project Beta", "Internal Tasks", "Client Meeting"]

# Sidebar - Add New Project
st.sidebar.header("Manage Projects")
new_project = st.sidebar.text_input("New Project Name")
if st.sidebar.button("Add Project"):
    if new_project and new_project not in project_options:
        project_options.append(new_project)
        pd.DataFrame(project_options, columns=["Project"]).to_csv(PROJECTS_FILE, index=False)
        st.sidebar.success(f"Added '{new_project}'")

# Load data or create empty
if os.path.exists(FILE_PATH):
    attendance_data = pd.read_csv(FILE_PATH)
    if "Employee" not in attendance_data.columns:
        attendance_data["Employee"] = "Unknown"
    if "Project" not in attendance_data.columns:
        attendance_data["Project"] = "Unknown"
else:
    attendance_data = pd.DataFrame(columns=["Employee", "Project", "Timestamp", "Action"])

def remove_last_entry(df, action):
    if df.empty:
        return df
    
    # Ensure Timestamp is datetime
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    current_date = datetime.now().date()
    
    # Find entries for today with the specific action
    today_entries = df[(df["Timestamp"].dt.date == current_date) & (df["Action"] == action)]
    
    if not today_entries.empty:
        # Remove the last entry found
        last_index = today_entries.index[-1]
        df = df.drop(last_index)
    return df

def check_entry_today(df, action, employee):
    if df.empty:
        return False
    timestamps = pd.to_datetime(df["Timestamp"])
    current_date = datetime.now().date()
    return ((timestamps.dt.date == current_date) & 
            (df["Action"] == action) & 
            (df["Employee"] == employee)).any()

def calculate_work_stats(df):
    if df.empty:
        return 0, 0
    
    # Work on a copy to ensure correct types and sorting without affecting the original
    df = df.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp")
    
    total_seconds = 0
    
    for _, group in df.groupby("Employee"):
        last_clock_in = None
        for _, row in group.iterrows():
            if row["Action"] == "Clock In":
                last_clock_in = row["Timestamp"]
            elif row["Action"] == "Clock Out" and last_clock_in:
                time_diff = row["Timestamp"] - last_clock_in
                total_seconds += time_diff.total_seconds()
                last_clock_in = None
            
    total_hours = total_seconds / 3600
    total_days = df.groupby("Employee")["Timestamp"].apply(lambda x: x.dt.date.nunique()).sum()
    
    return total_hours, total_days

def calculate_project_stats(df):
    if df.empty:
        return pd.DataFrame(columns=["Total Hours", "Total Days"])
    
    df = df.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values(["Employee", "Timestamp"])
    
    project_stats = {}
    
    for _, group in df.groupby("Employee"):
        last_clock_in = None
        last_project = None
        
        for _, row in group.iterrows():
            if row["Action"] == "Clock In":
                last_clock_in = row["Timestamp"]
                last_project = row["Project"]
            elif row["Action"] == "Clock Out" and last_clock_in is not None:
                project = last_project if last_project else "Unknown"
                duration = (row["Timestamp"] - last_clock_in).total_seconds() / 3600
                
                if project not in project_stats:
                    project_stats[project] = {"Total Hours": 0.0, "Days Set": set()}
                
                project_stats[project]["Total Hours"] += duration
                project_stats[project]["Days Set"].add(row["Timestamp"].date())
                
                last_clock_in = None
                last_project = None

    data = [{"Project": p, "Total Hours": s["Total Hours"], "Total Days": len(s["Days Set"])} for p, s in project_stats.items()]
    
    return pd.DataFrame(data).set_index("Project") if data else pd.DataFrame(columns=["Total Hours", "Total Days"])

# Sidebar - About
with st.sidebar.expander("About"):
    st.info("This app tracks employee attendance. Use the sidebar to correct entries.")

# Attendance Actions
with st.expander("Attendance Actions", expanded=True):
    project_name = st.selectbox("Project Name", project_options)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clock In"):
            if not employee_name:
                st.error("Please enter Employee Name.")
            elif check_entry_today(attendance_data, "Clock In", employee_name):
                st.warning("You have already clocked in today.")
            else:
                new_record = pd.DataFrame([{"Employee": employee_name, "Project": project_name, "Timestamp": datetime.now(), "Action": "Clock In"}])
                attendance_data = pd.concat([attendance_data, new_record], ignore_index=True)
                attendance_data.to_csv(FILE_PATH, index=False)
                st.success("Clocked In Successfully")
    with col2:
        if st.button("Clock Out"):
            if not employee_name:
                st.error("Please enter Employee Name.")
            elif check_entry_today(attendance_data, "Clock Out", employee_name):
                st.warning("You have already clocked out today.")
            else:
                new_record = pd.DataFrame([{"Employee": employee_name, "Project": project_name, "Timestamp": datetime.now(), "Action": "Clock Out"}])
                attendance_data = pd.concat([attendance_data, new_record], ignore_index=True)
                attendance_data.to_csv(FILE_PATH, index=False)
                st.success("Clocked Out Successfully")

if st.sidebar.button("Remove Last Clock In"):
    attendance_data = remove_last_entry(attendance_data, "Clock In")
    attendance_data.to_csv(FILE_PATH, index=False)
    st.sidebar.success("Last Clock In removed.")

if st.sidebar.button("Remove Last Clock Out"):
    attendance_data = remove_last_entry(attendance_data, "Clock Out")
    attendance_data.to_csv(FILE_PATH, index=False)
    st.sidebar.success("Last Clock Out removed.")

# Displaying Attendance Records
with st.expander("Attendance Records"):
    if not attendance_data.empty:
        attendance_data["Timestamp"] = pd.to_datetime(attendance_data["Timestamp"])
        
        def highlight_late(row):
            if row["Action"] == "Clock In" and row["Timestamp"].time() > datetime.strptime("09:00", "%H:%M").time():
                return ['background-color: #ffcccc'] * len(row)
            return [''] * len(row)
        st.dataframe(attendance_data.style.apply(highlight_late, axis=1))
    else:
        st.dataframe(attendance_data)

# Summary Statistics
with st.expander("Work Summary"):
    total_hours, total_days = calculate_work_stats(attendance_data)
    col1, col2 = st.columns(2)
    col1.metric("Total Days Worked", f"{total_days}")
    col2.metric("Total Hours Worked", f"{total_hours:.2f}")

with st.expander("Project Statistics"):
    project_stats_df = calculate_project_stats(attendance_data)
    st.bar_chart(project_stats_df)
