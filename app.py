import streamlit as st
import pandas as pd

st.title("نظام توزيع حصص الاحتياط 🏫")

# 1. رفع ملف الجدول
uploaded_file = st.file_uploader("ارفع جدول المدرسين (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # 2. إدخال بيانات الغياب
    absent_teacher = st.selectbox("المدرس الغائب:", df['Teacher_Name'].unique())
    day = st.selectbox("اليوم:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Sunday"])
    
    # تحديد الحصص اللي المدرس الغايب كان عنده فيها شغل
    teacher_row = df[df['Teacher_Name'] == absent_teacher]
    busy_periods = [col for col in df.columns if "Period" in col and teacher_row[col].values[0] != "Free"]

    st.subheader(f"الحصص المطلوبة للمدرس {absent_teacher}:")
    
    for period in busy_periods:
        class_name = teacher_row[period].values[0]
        # البحث عن المدرسين اللي عندهم الحصة دي "Free"
        available = df[df[period] == "Free"]['Teacher_Name'].tolist()
        
        st.write(f"📍 **الحصة {period} (فصل {class_name}):**")
        if available:
            selected_sub = st.selectbox(f"اختر بديل للحصة {period}", available, key=period)
        else:
            st.error("لا يوجد مدرسين متاحين في هذه الحصة!")

---