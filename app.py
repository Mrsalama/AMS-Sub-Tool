import streamlit as st
import pandas as pd
import os
import random

# Page configuration
st.set_page_config(page_title="AMS Smart Sub Tool", page_icon="🏫", layout="wide")

# Your background image link
bg_img_url = "https://img1.wsimg.com/isteam/ip/d03b28ee-bce7-4c2e-abac-d1a2150c0744/AMS%20COVER.jpg/:/cr=t:0%25,l:0%25,w:100%25,h:100%25/rs=w:890,cg:true"

# Advanced CSS for high contrast and dark table styling
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), url("{bg_img_url}");
        background-attachment: fixed;
        background-size: cover;
    }}
    .main .block-container {{ background-color: transparent; padding-top: 1rem; }}
    .dark-title {{ color: #001a33 !important; font-weight: 800; font-size: 38px; margin-bottom: 5px; }}
    .sub-card {{ background-color: #ffffff; padding: 25px; border-radius: 15px; border: 2px solid #002e5d; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; margin-bottom: 20px; }}
    .session-header {{ background-color: #002e5d; color: #ffffff !important; font-weight: bold; font-size: 20px; padding: 8px; border-radius: 8px; }}
    .teacher-name {{ color: #d32f2f !important; font-size: 22px; font-weight: bold; }}
    
    /* Style for the full table display */
    .styled-table {{ color: #001a33 !important; font-weight: bold; }}
    [data-testid="stSidebar"] label {{ color: white !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='dark-title'>🏫 AMS Smart Substitution System</h1>", unsafe_allow_html=True)

file_name = "school_schedule.xlsx"

if os.path.exists(file_name):
    # Load and clean data
    df = pd.read_excel(file_name).fillna('')
    df.columns = df.columns.str.strip()
    
    # Pre-processing: Rename Columns for display if they start with P
    display_df = df.copy()
    display_df.columns = [col.replace('P', 'Session ') if col.startswith('P') else col for col in display_df.columns]

    with st.sidebar:
        st.markdown("<h2 style='color:white;'>Management</h2>", unsafe_allow_html=True)
        teacher_options = ["-- Full Schedule --"] + list(df['Teacher_Name'].unique())
        absent_teacher = st.selectbox("Select Absent Teacher:", teacher_options)
        refresh_trigger = st.button("🔄 Shuffle Substitutes")

    if absent_teacher == "-- Full Schedule --":
        st.markdown("<h3 style='color:#002e5d;'>Current Staff Schedule</h3>", unsafe_allow_html=True)
        # Displaying the table with dark text
        st.dataframe(display_df.style.set_properties(**{'color': 'black', 'font-weight': 'bold', 'border-color': '#002e5d'}))
    else:
        # Substitution Logic
        periods = [col for col in df.columns if col.startswith('P')]
        teacher_info = df[df['Teacher_Name'] == absent_teacher].iloc[0]
        absent_grade = teacher_info['Grade'] if 'Grade' in df.columns else None
        
        busy_periods = [p for p in periods if str(teacher_info[p]).lower() != 'free' and str(teacher_info[p]).strip() != '']

        if busy_periods:
            st.markdown(f"<h3 style='color:#002e5d;'>Required Covers for: <span style='color:#d32f2f;'>{absent_teacher}</span></h3>", unsafe_allow_html=True)
            cols = st.columns(len(busy_periods))
            
            for i, p in enumerate(busy_periods):
                class_label = teacher_info[p]
                
                # Intelligent Search for Substitute
                # 1. Look for 'Free' teachers in the same Grade
                same_grade_subs = df[(df[p].astype(str).str.lower() == 'free') & (df['Grade'] == absent_grade)]['Teacher_Name'].tolist()
                # 2. Look for 'Free' teachers in other Grades (Backup)
                other_grade_subs = df[(df[p].astype(str).str.lower() == 'free') & (df['Grade'] != absent_grade)]['Teacher_Name'].tolist()
                
                # Priority Selection
                available_subs = same_grade_subs if same_grade_subs else other_grade_subs
                
                with cols[i]:
                    st.markdown(f"""<div class="sub-card">
                        <div class="session-header">Session {p.replace('P','')}</div>
                        <div style="color:#002e5d; margin-top:10px;">Class: <b>{class_label}</b></div>
                        <p style="color:#555; font-size:12px; margin-top:10px;">SUGGESTED SUBSTITUTE</p>""", unsafe_allow_html=True)
                    
                    if available_subs:
                        chosen = random.choice(available_subs)
                        # Mark if it's from the same grade or backup
                        grade_tag = "(Same Grade)" if chosen in same_grade_subs else "(Backup Grade)"
                        st.markdown(f'<div class="teacher-name">👤 {chosen}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="color:green; font-size:11px;">{grade_tag}</div>', unsafe_allow_html=True)
                    else:
                        st.error("No one free")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success(f"{absent_teacher} has no classes to cover.")

else:
    st.error("Please upload 'school_schedule.xlsx' with 'Teacher_Name', 'Grade', and 'P1-P8' columns.")
