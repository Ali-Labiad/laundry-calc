import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة والجماليات
st.set_page_config(page_title="Laundro-Sim Pro v7.0 (Final)", layout="wide")

def fix_ar(text):
    try: return get_display(reshape(text))
    except: return text

# 2. طبقة قاعدة البيانات (SQLite Persistence Layer)
DB_FILE = "laundry_final.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value REAL)''')
    conn.commit()
    conn.close()

def save_to_db(key, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def load_from_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings")
    data = {k: (int(v) if v == int(v) else v) for k, v in c.fetchall()}
    conn.close()
    return data

# 3. تهيئة البيانات (Initialization)
init_db()
db_cache = load_from_db()

DEFAULTS = {
    'n_w1': 3, 'p_w1': 180000, 'w1_p': 50, 'w1_c': 110, 'w1_d': 12,
    'n_w2': 2, 'p_w2': 320000, 'w2_p': 70, 'w2_c': 180, 'w2_d': 8,
    'n_dr': 3, 'p_dr': 150000, 'd_up': 100, 'd_ec': 15, 'd_ua': 2.0,
    'd_pm': 30, 'sal': 35000, 'f_ex': 10000, 'other_inv': 200000, 'dep_years': 5
}

def sync_data(key):
    val = st.session_state[f"ui_{key}"]
    save_to_db(key, val)
    st.session_state[key] = val

for key, def_val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = db_cache.get(key, def_val)

# --- الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.title("🛠️ التحكم والإصدار")
    st.info("النسخة النهائية: **v7.0**")
    st.write("---")
    if st.button("🗑️ تصفير كافة البيانات", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        conn.cursor().execute("DELETE FROM settings")
        conn.commit()
        conn.close()
        st.rerun()
    st.write("---")
    st.caption("تم تفعيل الحفظ التلقائي عبر SQLite")

# --- الواجهة الرئيسية ---
st.title("🚀 محاكي المغسلة الذكية")
st.success(f"مرحباً بك! جميع التغييرات تُحفظ تلقائياً في `{DB_FILE}`")

# --- القسم الأول: الأصول والاستثمار ---
with st.expander("🏗️ 1. هيكل الاستثمار (الأصول الثابتة)", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🧺 غسالات 12kg")
        st.number_input("العدد", value=int(st.session_state.n_w1), step=1, key="ui_n_w1", on_change=sync_data, args=("n_w1",))
        st.number_input("سعر الجهاز الواحد (دج)", value=int(st.session_state.p_w1), step=1000, key="ui_p_w1", on_change=sync_data, args=("p_w1",))
    with c2:
        st.markdown("### 🐘 غسالات 18kg")
        st.number_input("العدد ", value=int(st.session_state.n_w2), step=1, key="ui_n_w2", on_change=sync_data, args=("n_w2",))
        st.number_input("سعر الجهاز الواحد (دج)", value=int(st.session_state.p_w2), step=1000, key="ui_p_w2", on_change=sync_data, args=("p_w2",))
    with c3:
        st.markdown("### 🔥 مجففات الغاز")
        st.number_input("العدد ", value=int(st.session_state.n_dr), step=1, key="ui_n_dr", on_change=sync_data, args=("n_dr",))
        st.number_input("سعر المجفف الواحد (دج)", value=int(st.session_state.p_dr), step=1000, key="ui_p_dr", on_change=sync_data, args=("p_dr",))

    st.divider()
    ca, cb = st.columns(2)
    st.session_state.other_inv = ca.number_input("مصاريف تأسيس إضافية (ديكور، سباكة)", value=int(st.session_state.other_inv), step=1000, key="ui_other_inv", on_change=sync_data, args=("other_inv",))
    st.session_state.dep_years = cb.slider("العمر الافتراضي لتجديد الأجهزة (سنوات)", 1, 15, value=int(st.session_state.dep_years), key="ui_dep_years", on_change=sync_data, args=("dep_years",))

# --- القسم الثاني: التشغيل والأسعار ---
st.header("💰 2. إدارة التشغيل والمداخيل")
o1, o2 = st.columns(2)
with o1:
    st.markdown("#### 🎫 أسعار الخدمات")
    st.number_input("سعر الغسلة (12kg)", value=int(st.session_state.w1_p), step=10, key="ui_w1_p", on_change=sync_data, args=("w1_p",))
    st.number_input("زبائن يومياً (12kg)", value=int(st.session_state.w1_d), step=1, key="ui_w1_d", on_change=sync_data, args=("w1_d",))
    st.write("---")
    st.number_input("سعر الغسلة (18kg)", value=int(st.session_state.w2_p), step=10, key="ui_w2_p", on_change=sync_data, args=("w2_p",))
    st.number_input("زبائن يومياً (18kg)", value=int(st.session_state.w2_d), step=1, key="ui_w2_d", on_change=sync_data, args=("w2_d",))

with o2:
    st.markdown("#### 🛠️ التكاليف الثابتة والتجفيف")
    st.number_input("سعر وحدة التجفيف (15د)", value=int(st.session_state.d_up), step=10, key="ui_d_up", on_change=sync_data, args=("d_up",))
    st.number_input("رواتب العمال شهرياً", value=int(st.session_state.sal), step=1000, key="ui_sal", on_change=sync_data, args=("sal",))
    st.number_input("الإيجار والفواتير", value=int(st.session_state.f_ex), step=1000, key="ui_f_ex", on_change=sync_data, args=("f_ex",))
    st.number_input("أيام العمل في الشهر", value=int(st.session_state.d_pm), min_value=1, max_value=31, key="ui_d_pm", on_change=sync_data, args=("d_pm",))

# --- محرك الحسابات المالي ---
n1, p1, n2, p2, n_dr, p_dr = st.session_state.n_w1, st.session_state.p_w1, st.session_state.n_w2, st.session_state.p_w2, st.session_state.n_dr, st.session_state.p_dr
total_investment = int((n1*p1) + (n2*p2) + (n_dr*p_dr) + st.session_state.other_inv)

maint_cost = 20
dryer_energy = 15
dry_net_per_cust = (st.session_state.d_ua * st.session_state.d_up) - (st.session_state.d_ua * dryer_energy)

profit_w1 = (st.session_state.w1_p + dry_net_per_cust) - (st.session_state.w1_c + maint_cost)
profit_w2 = (st.session_state.w2_p + dry_net_per_cust) - (st.session_state.w2_c + maint_cost)

monthly_gross = ((profit_w1 * st.session_state.w1_d) + (profit_w2 * st.session_state.w2_d)) * st.session_state.d_pm
monthly_depreciation = (total_investment - st.session_state.other_inv) / (max(st.session_state.dep_years, 1) * 12)
net_profit_final = int(monthly_gross - (st.session_state.sal + st.session_state.f_ex + monthly_depreciation))

# --- لوحة النتائج النهائية ---
st.divider()
k1, k2, k3, k4 = st.columns(4)

k1.metric("صافي الربح الحقيقي", f"{max(net_profit_final, 0):,} دج")
k2.metric("إجمالي الاستثمار", f"{total_investment:,} دج")
k3.metric("فترة الاسترداد", f"{total_investment/net_profit_final if net_profit_final > 0 else 0:.1f} شهر")
k4.metric("الإهلاك الشهري", f"{int(monthly_depreciation):,} دج")
