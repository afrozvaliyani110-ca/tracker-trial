import streamlit as st
import pandas as pd
import datetime
import json
import os

# --- Configuration & Setup ---
st.set_page_config(
    page_title="CA Final Tracker by Afroz",
    page_icon="📚",
    layout="wide"
)

# File path to save user data
DATA_FILE = "study_data.json"

# Default Data Structure (Updated with Lectures/Hours and 4 SPOM sets)
DEFAULT_DATA = {
    "subjects": {
        "Paper 1: Financial Reporting": {"total_lecs": 0, "done_lecs": 0, "total_ch": 20, "completed_ch": 0, "revisions": 0},
        "Paper 2: AFM": {"total_lecs": 0, "done_lecs": 0, "total_ch": 15, "completed_ch": 0, "revisions": 0},
        "Paper 3: Adv. Auditing": {"total_lecs": 0, "done_lecs": 0, "total_ch": 18, "completed_ch": 0, "revisions": 0},
        "Paper 4: Direct Tax": {"total_lecs": 0, "done_lecs": 0, "total_ch": 25, "completed_ch": 0, "revisions": 0},
        "Paper 5: Indirect Tax": {"total_lecs": 0, "done_lecs": 0, "total_ch": 12, "completed_ch": 0, "revisions": 0},
        "Paper 6: IBS (Multi-disp)": {"total_lecs": 0, "done_lecs": 0, "total_ch": 10, "completed_ch": 0, "revisions": 0},
    },
    "spom": {
        "Set A: Corp & Eco Laws": {"status": False, "marks": 0},
        "Set B: SCMPE": {"status": False, "marks": 0},
        "Set C: Elective": {"status": False, "marks": 0},
        "Set D: Multi-disciplinary": {"status": False, "marks": 0},
    },
    "settings": {
        "exam_date": str(datetime.date.today() + datetime.timedelta(days=180)),
        "articleship_date": str(datetime.date.today() + datetime.timedelta(days=365)),
        "name": "Afroz"
    },
    "notes": ""
}

# --- Helper Functions ---
def load_data():
    """Loads data and merges with defaults to prevent errors if structure changes"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            saved_data = json.load(f)
            # Merge logic: Ensure new keys exist in old files
            # 1. Check Subjects
            for sub, details in DEFAULT_DATA['subjects'].items():
                if sub not in saved_data['subjects']:
                    saved_data['subjects'][sub] = details
                else:
                    # Ensure new lecture fields exist
                    if 'total_lecs' not in saved_data['subjects'][sub]:
                        saved_data['subjects'][sub]['total_lecs'] = 0
                        saved_data['subjects'][sub]['done_lecs'] = 0
            # 2. Check SPOM
            for set_name, details in DEFAULT_DATA['spom'].items():
                if set_name not in saved_data['spom']:
                    saved_data['spom'][set_name] = details
            
            return saved_data
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- Load State ---
if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# --- Sidebar: Settings & Key Dates ---
with st.sidebar:
    st.header(f"👨‍🎓 {data['settings']['name']}'s Settings")
    
    # Date Inputs
    try:
        default_exam = datetime.datetime.strptime(data['settings']['exam_date'], "%Y-%m-%d").date()
        default_art = datetime.datetime.strptime(data['settings']['articleship_date'], "%Y-%m-%d").date()
    except:
        default_exam = datetime.date.today()
        default_art = datetime.date.today()

    exam_date = st.date_input("Target Exam Date", value=default_exam)
    art_date = st.date_input("Articleship End Date", value=default_art)
    
    # Save Dates
    if st.button("Update Dates"):
        data['settings']['exam_date'] = str(exam_date)
        data['settings']['articleship_date'] = str(art_date)
        save_data(data)
        st.success("Dates Saved!")

    st.markdown("---")
    st.markdown("### 💡 Motivation")
    st.info('"Success is the sum of small efforts, repeated day in and day out."')

# --- Main Page Header ---
st.title(f"📊 CA Final Tracker by {data['settings']['name']}")
st.markdown("Track your Main Subjects, SPOM (All 4 Sets), and Articleship progress.")

# --- Dashboard Metrics ---
col1, col2, col3 = st.columns(3)

today = datetime.date.today()
days_to_exam = (exam_date - today).days
days_to_freedom = (art_date - today).days

# Calculate Total Syllabus Progress (Based on Chapters)
total_chapters = sum(d['total_ch'] for d in data['subjects'].values())
completed_chapters = sum(d['completed_ch'] for d in data['subjects'].values())
progress_pct = (completed_chapters / total_chapters) if total_chapters > 0 else 0

with col1:
    st.metric(label="⏳ Days to Exam", value=f"{days_to_exam} Days")
with col2:
    st.metric(label="🏢 Days to Articleship End", value=f"{days_to_freedom} Days")
with col3:
    st.metric(label="📈 Chapter Completion", value=f"{int(progress_pct * 100)}%")

st.progress(progress_pct)

# --- Tabs for Details ---
tab1, tab2, tab3 = st.tabs(["📚 Main Subjects Tracker", "💻 SPOM (4 Sets)", "📝 Notes & Strategy"])

# --- TAB 1: Main Subjects Tracking ---
with tab1:
    st.subheader("Detailed Subject Tracking")
    st.caption("Enter Hours OR Number of Lectures in the 'Total' and 'Done' columns.")
    
    # We convert the JSON dict to a Pandas DataFrame for easy editing
    df_data = []
    for subject, details in data['subjects'].items():
        row = {
            "Subject": subject,
            "Total Lecs/Hrs": details.get('total_lecs', 0),
            "Done Lecs/Hrs": details.get('done_lecs', 0),
            "Total Chapters": details['total_ch'],
            "Chapters Done": details['completed_ch'],
            "Revisions Done": details['revisions']
        }
        df_data.append(row)
    
    df = pd.DataFrame(df_data)

    # Configure the editable dataframe
    edited_df = st.data_editor(
        df,
        column_config={
            "Subject": st.column_config.TextColumn("Subject", disabled=True),
            "Total Lecs/Hrs": st.column_config.NumberColumn("Total Lecs/Hrs", min_value=0, max_value=500, help="Total Number of Lectures or Hours"),
            "Done Lecs/Hrs": st.column_config.NumberColumn("Done Lecs/Hrs", min_value=0, max_value=500, help="Completed Lectures or Hours"),
            "Total Chapters": st.column_config.NumberColumn("Total Ch.", min_value=1, max_value=100),
            "Chapters Done": st.column_config.NumberColumn("Done Ch.", min_value=0, max_value=100),
            "Revisions Done": st.column_config.NumberColumn("Revisions", min_value=0, max_value=10, format="%d 🔄"),
        },
        use_container_width=True,
        hide_index=True,
        key="editor"
    )

    # Calculate Lecture Completion % for display
    total_lecs_all = edited_df["Total Lecs/Hrs"].sum()
    done_lecs_all = edited_df["Done Lecs/Hrs"].sum()
    if total_lecs_all > 0:
        lec_pct = int((done_lecs_all / total_lecs_all) * 100)
        st.info(f"🎥 Overall Video/Class Completion: **{lec_pct}%** ({done_lecs_all}/{total_lecs_all})")

    # Save Logic for DataFrame
    if st.button("Save Subject Progress"):
        for index, row in edited_df.iterrows():
            sub_name = row['Subject']
            data['subjects'][sub_name]['total_lecs'] = row['Total Lecs/Hrs']
            data['subjects'][sub_name]['done_lecs'] = row['Done Lecs/Hrs']
            data['subjects'][sub_name]['total_ch'] = row['Total Chapters']
            data['subjects'][sub_name]['completed_ch'] = row['Chapters Done']
            data['subjects'][sub_name]['revisions'] = row['Revisions Done']
        
        save_data(data)
        st.toast("Subject Progress Saved!", icon="✅")
        st.rerun()

# --- TAB 2: SPOM & Exam Status ---
with tab2:
    st.subheader("SPOM (Self-Paced Online Modules)")
    
    # Create 2x2 Grid for 4 Sets
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    spom_keys = list(data['spom'].keys())
    
    # Helper to create SPOM card
    def spom_card(col, set_name, key_suffix):
        with col:
            st.markdown(f"#### {set_name}")
            status = st.checkbox("Exam Cleared ✅", value=data['spom'][set_name]['status'], key=f"status_{key_suffix}")
            marks = st.number_input("Marks Obtained", value=data['spom'][set_name]['marks'], key=f"marks_{key_suffix}")
            if status:
                st.success(f"Cleared {set_name}!")
            return status, marks

    # Render Cards
    s1, m1 = spom_card(row1_col1, "Set A: Corp & Eco Laws", "a")
    s2, m2 = spom_card(row1_col2, "Set B: SCMPE", "b")
    st.markdown("---") # Divider
    s3, m3 = spom_card(row2_col1, "Set C: Elective", "c")
    s4, m4 = spom_card(row2_col2, "Set D: Multi-disciplinary", "d")

    # Save SPOM
    if st.button("Update SPOM Status"):
        data['spom']['Set A: Corp & Eco Laws'] = {'status': s1, 'marks': m1}
        data['spom']['Set B: SCMPE'] = {'status': s2, 'marks': m2}
        data['spom']['Set C: Elective'] = {'status': s3, 'marks': m3}
        data['spom']['Set D: Multi-disciplinary'] = {'status': s4, 'marks': m4}
        save_data(data)
        st.toast("SPOM Data Saved!", icon="💾")
        st.rerun()

# --- TAB 3: Notes & Quick Links ---
with tab3:
    st.subheader("My Study Notes & To-Do")
    
    notes = st.text_area("Jot down topics to review or daily goals:", value=data['notes'], height=200)
    
    if st.button("Save Notes"):
        data['notes'] = notes
        save_data(data)
        st.success("Notes saved.")

    st.markdown("---")
    st.markdown("### 🔗 Quick Resources")
    st.markdown("- [ICAI BOS Portal](https://www.icai.org/)")
    st.markdown("- [SPOM Learning Portal](https://lms.icai.org/)")

# Footer
st.markdown("---")
st.caption("Keep pushing, CA Afroz! The prefix is waiting for you.")