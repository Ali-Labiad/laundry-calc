import streamlit as st
import sqlite3
import pandas as pd

# 1. إعداد قاعدة البيانات (Database Layer)
DB_FILE = "laundry_settings.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # إنشاء جدول لحفظ المفاتيح والقيم
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value REAL)''')
    conn.commit()
    conn.close()

def save_setting(key, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def load_settings():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings")
    data = dict(c.fetchall())
    conn.close()
    return data

# 2. تهيئة التطبيق
st.set_page_config(page_title="Laundro-Sim Pro SQL", layout="wide")
init_db()
db_data = load_settings()

# قيم افتراضية في حال كانت القاعدة فارغة
DEFAULTS = {
    'w1_p': 250.0, 'w1_d': 12.0, 'w1_c': 110.0,
    'w2_p': 450.0, 'w2_d': 8.0, 'w2_c': 180.0,
    'n_w1': 3.0, 'p_w1': 180000.0,
    'sal': 35000.0, 'f_ex': 10000.0, 'd_pm': 30.0
}

# دالة وسيطة لتحديث القاعدة والـ session_state معاً
def sync_change(key):
    new_val = st.session_state[f"input_{key}"]
    save_setting(key, new_val)
    st.session_state[key] = new_val

# تحميل البيانات من SQL إلى Session State عند بدء التشغيل
for key, def_val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = db_data.get(key, def_val)

st.title("🗄️ محاكي المغسلة المدعوم بقاعدة بيانات SQLite")
st.info("✅ جميع التغييرات تُحفظ تلقائياً في ملف `laundry_settings.db` ولا تضيع بالـ Refresh.")

# --- واجهة المستخدم ---
with st.expander("🏗️ الاستثمار والأجهزة (محفوظة في SQL)", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        # نستخدم on_change لضمان الحفظ في SQL فور التغيير
        n_w1 = st.number_input("عدد غسالات 12kg", 
                               value=float(st.session_state.n_w1), 
                               key="input_n_w1", 
                               on_change=sync_change, args=("n_w1",))
        
        p_w1 = st.number_input("سعر الغسالة (دج)", 
                               value=float(st.session_state.p_w1), 
                               key="input_p_w1", 
                               on_change=sync_change, args=("p_w1",))

    with col2:
        sal = st.number_input("رواتب العمال شهرياً", 
                              value=float(st.session_state.sal), 
                              key="input_sal", 
                              on_change=sync_change, args=("sal",))
        
        f_ex = st.number_input("إيجار ومصاريف ثابتة", 
                               value=float(st.session_state.f_ex), 
                               key="input_f_ex", 
                               on_change=sync_change, args=("f_ex",))

# --- منطق الحسابات ---
total_inv = st.session_state.n_w1 * st.session_state.p_w1
# (يمكنك إكمال باقي الحسابات هنا بنفس الطريقة)

st.divider()
st.metric("إجمالي الاستثمار الحالي", f"{total_inv:,.0f} دج")

# زر لمسح قاعدة البيانات والبدء من جديد
if st.sidebar.button("⚠️ تصفير قاعدة البيانات"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM settings")
    conn.commit()
    conn.close()
    st.rerun()
