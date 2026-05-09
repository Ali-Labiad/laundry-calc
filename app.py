import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro SQL Edition", layout="wide")

def fix_ar(text):
    try: return get_display(reshape(text))
    except: return text

# 2. طبقة قاعدة البيانات (SQLite Layer)
DB_FILE = "laundry_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS laundry_settings
                 (key TEXT PRIMARY KEY, value REAL)''')
    conn.commit()
    conn.close()

def save_to_db(key, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO laundry_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def load_all_from_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT key, value FROM laundry_settings")
    data = dict(c.fetchall())
    conn.close()
    return data

# 3. تهيئة البيانات (Initialization)
init_db()
db_cache = load_all_from_db()

# القيم الافتراضية الأصلية
DEFAULTS = {
    'n_w1': 3, 'p_w1': 180000, 'w1_p': 50, 'w1_c': 110, 'w1_d': 12,
    'n_w2': 2, 'p_w2': 320000, 'w2_p': 70, 'w2_c': 180, 'w2_d': 8,
    'n_dr': 3, 'p_dr': 150000, 'd_up': 100, 'd_ec': 15, 'd_ua': 2.0,
    'd_pm': 30, 'sal': 35000, 'f_ex': 10000, 'other_inv': 200000, 'dep_years': 5
}

# دالة مزامنة التغييرات
def sync_db(key):
    # تحديث الذاكرة الدائمة وقاعدة البيانات فوراً
    val = st.session_state[f"ui_{key}"]
    save_to_db(key, val)
    st.session_state[key] = val

# تحميل البيانات من SQL إلى Session State
for key, def_val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = db_cache.get(key, def_val)

st.title("🚀 محاكي المغسلة الذكية - نسخة SQL المستقرة")
st.info("💾 جميع البيانات محفوظة في `laundry_data.db`. التحديث (Refresh) لن يمسح مدخلاتك.")

# --- القسم الأول: الأصول (Assets) ---
with st.expander("🏗️ 1. هيكل الاستثمار (قاعدة البيانات نشطة)", expanded=True):
    c_inv1, c_inv2, c_inv3 = st.columns(3)
    with c_inv1:
        st.markdown("### 🧺 غسالات 12kg")
        st.number_input("العدد", value=float(st.session_state.n_w1), key="ui_n_w1", on_change=sync_db, args=("n_w1",))
        st.number_input("السعر (دج)", value=float(st.session_state.p_w1), key="ui_p_w1", on_change=sync_db, args=("p_w1",))
    with c_inv2:
        st.markdown("### 🐘 غسالات 18kg")
        st.number_input("العدد ", value=float(st.session_state.n_w2), key="ui_n_w2", on_change=sync_db, args=("n_w2",))
        st.number_input("السعر  (دج)", value=float(st.session_state.p_w2), key="ui_p_w2", on_change=sync_db, args=("p_w2",))
    with c_inv3:
        st.markdown("### 🔥 مجففات الغاز")
        st.number_input("العدد  ", value=float(st.session_state.n_dr), key="ui_n_dr", on_change=sync_db, args=("n_dr",))
        st.number_input("السعر   (دج)", value=float(st.session_state.p_dr), key="ui_p_dr", on_change=sync_db, args=("p_dr",))

    st.divider()
    c_inv_a, c_inv_b = st.columns(2)
    st.session_state.other_inv = c_inv_a.number_input("مصاريف تأسيس أخرى", value=float(st.session_state.other_inv), key="ui_other_inv", on_change=sync_db, args=("other_inv",))
    st.session_state.dep_years = c_inv_b.slider("سنوات الإهلاك", 1, 15, value=int(st.session_state.dep_years), key="ui_dep_years", on_change=sync_db, args=("dep_years",))

# --- القسم الثاني: التشغيل ---
st.header("💰 2. التشغيل والأسعار")
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    st.number_input("سعر غسلة (12kg)", value=float(st.session_state.w1_p), key="ui_w1_p", on_change=sync_db, args=("w1_p",))
    st.number_input("زبائن (12kg) يومياً", value=float(st.session_state.w1_d), key="ui_w1_d", on_change=sync_db, args=("w1_d",))
    st.number_input("تكلفة منظفات (12kg)", value=float(st.session_state.w1_c), key="ui_w1_c", on_change=sync_db, args=("w1_c",))
    st.write("---")
    st.number_input("سعر غسلة (18kg)", value=float(st.session_state.w2_p), key="ui_w2_p", on_change=sync_db, args=("w2_p",))
    st.number_input("زبائن (18kg) يومياً", value=float(st.session_state.w2_d), key="ui_w2_d", on_change=sync_db, args=("w2_d",))

with col_opt2:
    st.number_input("سعر وحدة التجفيف", value=float(st.session_state.d_up), key="ui_d_up", on_change=sync_db, args=("d_up",))
    st.number_input("الرواتب الشهرية", value=float(st.session_state.sal), key="ui_sal", on_change=sync_db, args=("sal",))
    st.number_input("إيجار ومصاريف ثابتة", value=float(st.session_state.f_ex), key="ui_f_ex", on_change=sync_db, args=("f_ex",))
    st.number_input("أيام التشغيل", value=float(st.session_state.d_pm), key="ui_d_pm", on_change=sync_db, args=("d_pm",))

# --- الحسابات المالية (Business Logic) ---
# جلب القيم الحالية من الذاكرة
n1, p1, n2, p2, n_dr, p_dr = st.session_state.n_w1, st.session_state.p_w1, st.session_state.n_w2, st.session_state.p_w2, st.session_state.n_dr, st.session_state.p_dr
total_investment = (n1*p1) + (n2*p2) + (n_dr*p_dr) + st.session_state.other_inv

maint = 20
dry_profit = (st.session_state.d_ua * st.session_state.d_up) - (st.session_state.d_ua * st.session_state.d_ec)
profit_w1 = (st.session_state.w1_p + dry_profit) - (st.session_state.w1_c + maint)
profit_w2 = (st.session_state.w2_p + dry_profit) - (st.session_state.w2_c + maint)

monthly_gross = ((profit_w1 * st.session_state.w1_d) + (profit_w2 * st.session_state.w2_d)) * st.session_state.d_pm
monthly_depreciation = (total_investment - st.session_state.other_inv) / (max(st.session_state.dep_years, 1) * 12)
net_profit = monthly_gross - (st.session_state.sal + st.session_state.f_ex + monthly_depreciation)

# --- لوحة النتائج ---
st.divider()
k1, k2, k3 = st.columns(3)
k1.metric("صافي الربح الحقيقي", f"{net_profit:,.0f} دج")
k2.metric("إجمالي الاستثمار", f"{total_investment:,.0f} دج")
k3.metric("فترة الاسترداد", f"{total_investment/net_profit if net_profit > 0 else 0:.1f} شهر")

# زر الحذف النهائي في الجانب
if st.sidebar.button("🗑️ تصفير كل البيانات (SQL)"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM laundry_settings")
    conn.commit()
    conn.close()
    st.rerun()
