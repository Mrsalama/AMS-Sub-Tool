import streamlit as st
import pandas as pd
import os
import random

# Page configuration
st.set_page_config(page_title="AMS Smart Sub Tool", page_icon="🏫", layout="wide")

bg_img_url = "https://img1.wsimg.com/isteam/ip/d03b28ee-bce7-4c2e-abac-d1a2150c0744/AMS%20COVER.jpg/:/cr=t:0%25,l:0%25,w:100%25,h:100%25/rs=w:890,cg:true"

# Advanced CSS for Dark Tables and Cards
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), url("{bg_img_url}");
        background-attachment: fixed;
        background-size: cover;
    }}
    .main .block-container {{ background-color: transparent; padding-top: 2rem; }}
    .dark-title {{ color: #001a33 !important; font-weight: 800; font-size: 42px; margin-bottom: 10px; }}
    .sub-card {{ background-color: #ffffff; padding: 25px; border-radius: 20px; border: 1px solid #e0e0e0; box-shadow: 0 10px 20px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px; }}
    .session-header {{ background-color: #002e5d; color: #ffffff !important; font-weight: 800; font-size: 22px; padding: 8px; border-radius: 10px; margin-bottom: 10px; }}
    .teacher-name {{ color: #d32f2f !important; font-size: 22px; font-weight: bold; }}
    
    /* Dark Table Styling */
    .stDataFrame {{
        background-color: #1e1e1e !important;
        border-radius: 15px;
        padding: 10px;
    }}
    div[data-testid="stTable"] {{ background-color: #1e1e1e; color: white; }}
    [data-testid="stSidebar"] label {{ color: white !important; font-weight: bold !important; }}
    [data-testid="stSidebar"] .stMarkdown p {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='dark-title'>🏫 AMS Smart Substitution System</h1>", unsafe_allow_html=True)

file_name = "school_schedule.xlsx"

if os.path.exists(file_name):
    # Load and clean data
    df = pd.read_excel(file_name).fillna('')
    df.columns = df.columns.str.strip()
    
    with st.sidebar:
        st.markdown("<h2 style='color:white;'>Management</h2>", unsafe_allow_html=True)
        teacher_options = ["-- Show Full Schedule --"] + list(df['Teacher_Name'].unique())
        absent_teacher = st.selectbox("Select Absent Teacher:", teacher_options)
        st.markdown("---")
        refresh_trigger = st.button("🔄 Shuffle Substitutes")

    # LOGIC: If no teacher selected, show the full table in dark mode
    if absent_teacher == "-- Show Full Schedule --":
        st.subheader("🗓️ Full Staff Schedule")
        # Displaying a styled dark dataframe
        st.dataframe(df.style.set_properties(**{
            'background-color': '#1e1e1e',
            'color': 'white',
            'border-color': '#444'
        }), use_container_width=True)
    else:
        # Substitution Process
        periods = [col for col in df.columns if col.startswith('P')]
        teacher_row = df[df['Teacher_Name'] == absent_teacher].iloc[0]
        absent_grade = teacher_row['Grade'] if 'Grade' in df.columns else ""
        
        busy_periods = [p for p in periods if str(teacher_row[p]).lower() != 'free' and str(teacher_row[p]).strip() != '']

        if busy_periods:
            st.markdown(f"<h3 style='color:#002e5d;'>Covers for: <span style='color:#d32f2f;'>{absent_teacher}</span></h3>", unsafe_allow_html=True)
            cols = st.columns(len(busy_periods))
            
            for i, p in enumerate(busy_periods):
                class_label = teacher_row[p]
                
                # Intelligent Search Logic:
                # 1. Find all free teachers for this period
                all_free = df[df[p].astype(str).str.lower() == 'free']
                
                if not all_free.empty:
                    # 2. Try to find teachers from the SAME GRADE first
                    if 'Grade' in df.columns:
                        same_grade = all_free[all_free['Grade'] == absent_grade]
                        if not same_grade.empty:
                            suggested_sub = random.choice(same_grade['Teacher_Name'].tolist())
                        else:
                            # 3. If not found, find from ANY other grade (the closest available)
                            suggested_sub = random.choice(all_free['Teacher_Name'].tolist())
                    else:
                        suggested_sub = random.choice(all_free['Teacher_Name'].tolist())
                else:
                    suggested_sub = None

                with cols[i]:
                    st.markdown(f"""<div class="sub-card">
                        <div class="session-header">Session {p.replace('P','')}</div>
                        <div style="color:#555; font-weight:bold;">Class: {class_label}</div>
                        <p style="color:#888; font-size:12px; margin-top:10px;">PROPOSED SUBSTITUTE</p>""", unsafe_allow_html=True)
                    if suggested_sub:
                        st.markdown(f'<div class="teacher-name">👤 {suggested_sub}</div>', unsafe_allow_html=True)
                    else:
                        st.error("No Staff Available")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if refresh_trigger:
                st.toast("Re-calculating best matches...")
        else:
            st.balloons()
            st.success(f"{absent_teacher} has no classes today.")
else:
    st.error("Please upload 'school_schedule.xlsx' to GitHub.")
