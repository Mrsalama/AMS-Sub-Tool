import streamlit as st
import pandas as pd
import os
import random

# Page configuration
st.set_page_config(page_title="AMS Smart Sub Tool", page_icon="🏫", layout="wide")

# Your background image link
bg_img_url = "https://img1.wsimg.com/isteam/ip/d03b28ee-bce7-4c2e-abac-d1a2150c0744/AMS%20COVER.jpg/:/cr=t:0%25,l:0%25,w:100%25,h:100%25/rs=w:890,cg:true"

# Advanced CSS for dark theme and high contrast
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), url("{bg_img_url}");
        background-attachment: fixed;
        background-size: cover;
    }}
    .main .block-container {{ background-color: transparent; padding-top: 2rem; }}
    .dark-title {{ color: #001a33 !important; font-weight: 800; font-size: 42px; margin-bottom: 10px; }}
    .dark-subtitle {{ color: #002e5d !important; font-weight: 700; font-size: 28px; margin-top: 20px; }}
    
    /* Table Styling */
    .styled-table {{ border-collapse: collapse; margin: 25px 0; font-size: 0.9em; min-width: 400px; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0, 0, 0, 0.15); }}
    
    /* Card Design */
    .sub-card {{ background-color: #ffffff; padding: 25px; border-radius: 20px; border: 1px solid #002e5d; box-shadow: 0 10px 20px rgba(0,0,0,0.1); text-align: center; margin-bottom: 20px; }}
    .session-header {{ background-color: #002e5d; color: #ffffff !important; font-weight: 800; font-size: 22px; padding: 8px; border-radius: 10px; margin-bottom: 12px; }}
    .class-name {{ color: #000000 !important; font-size: 20px; font-weight: 700; margin-top: 8px; }}
    .teacher-name {{ color: #d32f2f !important; font-size: 22px; font-weight: bold; border: 2px solid #d32f2f; padding: 5px; border-radius: 10px; display: inline-block; }}
    
    .white-text {{ color: #ffffff !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); font-weight: bold; }}
    [data-testid="stSidebar"] label {{ color: white !important; font-size: 18px !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='dark-title'>🏫 AMS Smart Substitution System</h1>", unsafe_allow_html=True)

file_name = "school_schedule.xlsx"

if os.path.exists(file_name):
    # Load and clean data
    df = pd.read_excel(file_name).fillna('')
    df.columns = df.columns.str.strip()

    with st.sidebar:
        st.markdown("<h2 class='white-text'>Management</h2>", unsafe_allow_html=True)
        teacher_options = ["-- View Full Schedule --"] + list(df['Teacher_Name'].unique())
        absent_teacher = st.selectbox("Select Absent Teacher:", teacher_options)
        st.markdown("---")
        refresh_trigger = st.button("🔄 Shuffle Substitutes")
        st.markdown("<p class='white-text'>System prioritizes substitutes from the same Grade level first.</p>", unsafe_allow_html=True)

    # logic to handle display
    if absent_teacher == "-- View Full Schedule --":
        st.markdown("<h3 class='dark-subtitle'>Full School Schedule</h3>", unsafe_allow_html=True)
        # Displaying the dataframe with dark colors
        st.dataframe(df.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border-color': '#002e5d'}))
    else:
        periods = [col for col in df.columns if col.startswith('P')]
        teacher_row = df[df['Teacher_Name'] == absent_teacher].iloc[0]
        
        # Get absent teacher's Grade/Level (Assuming it's in a column named 'Grade' or 'Level')
        # If no such column, we try to extract from class name like 'G1'
        absent_grade = str(teacher_row.get('Grade', '')) 

        busy_periods = [p for p in periods if str(teacher_row[p]).lower() != 'free' and str(teacher_row[p]).strip() != '']

        if busy_periods:
            st.markdown(f"<h3 class='dark-subtitle'>Substitution Plan for: <span style='color:#d32f2f;'>{absent_teacher}</span></h3>", unsafe_allow_html=True)
            cols = st.columns(len(busy_periods))
            
            for i, p in enumerate(busy_periods):
                class_label = teacher_row[p]
                
                # Logic: Find available teachers
                all_available = df[df[p].astype(str).str.lower() == 'free']
                
                # 1. Try same Grade
                if 'Grade' in df.columns:
                    same_grade_available = all_available[all_available['Grade'] == absent_grade]['Teacher_Name'].tolist()
                else:
                    same_grade_available = []

                with cols[i]:
                    st.markdown(f'<div class="sub-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="session-header">Session {p.replace("P","")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="class-name">Class: {class_label}</div>', unsafe_allow_html=True)
                    st.markdown('<p style="color: #444; margin-top:10px; font-weight:bold;">Assigned Substitute:</p>', unsafe_allow_html=True)

                    if not all_available.empty:
                        # Priority selection
                        if same_grade_available:
                            suggested_sub = random.choice(same_grade_available)
                            st.markdown(f'<div class="teacher-name">👤 {suggested_sub}</div>', unsafe_allow_html=True)
                            st.caption("✨ Same Grade Match")
                        else:
                            # If no same grade, pick any available
                            suggested_sub = random.choice(all_available['Teacher_Name'].tolist())
                            st.markdown(f'<div class="teacher-name">👤 {suggested_sub}</div>', unsafe_allow_html=True)
                            st.caption("ℹ️ Cross-Grade Match")
                    else:
                        st.error("No Staff Available")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if refresh_trigger:
                st.toast("Regenerating smart matches...")
        else:
            st.balloons()
            st.success(f"Teacher {absent_teacher} is free today!")
else:
    st.error(f"File '{file_name}' not found.")
