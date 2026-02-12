import streamlit as st
import pandas as pd
import os
import random

# Page configuration
st.set_page_config(page_title="AMS Smart Sub Tool", page_icon="🏫", layout="wide")

# Your background image link
bg_img_url = "https://img1.wsimg.com/isteam/ip/d03b28ee-bce7-4c2e-abac-d1a2150c0744/AMS%20COVER.jpg/:/cr=t:0%25,l:0%25,w:100%25,h:100%25/rs=w:890,cg:true"

# Refined Professional Style
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), url("{bg_img_url}");
        background-attachment: fixed;
        background-size: cover;
    }}
    .main .block-container {{ background-color: transparent; padding-top: 2rem; }}
    .dark-title {{ color: #001a33 !important; font-weight: 800; font-size: 42px; margin-bottom: 10px; }}
    .dark-subtitle {{ color: #002e5d !important; font-weight: 700; font-size: 28px; margin-top: 20px; }}
    .sub-card {{ background-color: #ffffff; padding: 30px; border-radius: 20px; border: 1px solid #e0e0e0; box-shadow: 0 10px 20px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px; }}
    .white-text {{ color: #ffffff !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }}
    .session-header {{ background-color: #002e5d; color: #ffffff !important; font-weight: 800; font-size: 24px; padding: 10px; border-radius: 10px; margin-bottom: 15px; }}
    .class-name {{ color: #333333 !important; font-size: 20px; font-weight: 600; margin-top: 10px; }}
    .teacher-name {{ color: #d32f2f !important; font-size: 24px; font-weight: bold; }}
    [data-testid="stSidebar"] label {{ color: white !important; font-size: 18px !important; font-weight: bold !important; }}
    [data-testid="stSidebar"] .stMarkdown p {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='dark-title'>🏫 AMS Smart Substitution System</h1>", unsafe_allow_html=True)

file_name = "school_schedule.xlsx"

if os.path.exists(file_name):
    # Read file and replace empty cells (nan) with empty string
    df = pd.read_excel(file_name).fillna('')
    
    with st.sidebar:
        st.markdown("<h2 class='white-text'>Management</h2>", unsafe_allow_html=True)
        
        # 1. New Day Selection
        selected_day = st.selectbox("Select Day of the Week:", df['Day'].unique())
        
        # Filter dataframe by selected day
        day_df = df[df['Day'] == selected_day]
        
        # 2. Select Teacher from filtered list
        absent_teacher = st.selectbox("Select Absent Teacher:", day_df['Teacher_Name'].unique())
        
        st.markdown("---")
        refresh_trigger = st.button("🔄 Shuffle Substitutes")
        st.markdown("<p class='white-text'>The system picks a substitute from available 'Free' staff for the selected teacher's sessions.</p>", unsafe_allow_html=True)

    # Process filtered day data
    periods = [col for col in df.columns if col.startswith('P')]
    teacher_row = day_df[day_df['Teacher_Name'] == absent_teacher].iloc[0]
    busy_periods = [p for p in periods if str(teacher_row[p]).lower() != 'free' and str(teacher_row[p]) != '']

    if busy_periods:
        st.markdown(f"<h3 class='dark-subtitle'>Covers for {absent_teacher} on {selected_day}:</h3>", unsafe_allow_html=True)
        cols = st.columns(len(busy_periods))
        
        for i, p in enumerate(busy_periods):
            class_label = teacher_row[p]
            # Find available teachers ON THE SAME DAY
            available_teachers = day_df[day_df[p].astype(str).str.lower() == 'free']['Teacher_Name'].tolist()
            
            with cols[i]:
                st.markdown(f"""<div class="sub-card">
                    <div class="session-header">Session {p.replace('P','')}</div>
                    <div class="class-name">Class: {class_label}</div>
                    <p style="color: #777; margin-top:15px; font-size:14px; text-transform:uppercase;">Assigned Substitute</p>""", unsafe_allow_html=True)
                
                if available_teachers:
                    suggested_sub = random.choice(available_teachers)
                    st.markdown(f'<div class="teacher-name">👤 {suggested_sub}</div>', unsafe_allow_html=True)
                else:
                    st.error("No Staff Available")
                st.markdown('</div>', unsafe_allow_html=True)
        
        if refresh_trigger:
            st.toast(f"Updating assignments for {selected_day}...")
    else:
        st.balloons()
        st.success(f"No classes found for {absent_teacher} on {selected_day}.")
else:
    st.error(f"Missing File: Please ensure '{file_name}' is uploaded.")
