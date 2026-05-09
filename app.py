import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro v6.5", layout="wide")

def fix_ar(text):
    try: return get_display(reshape(text))
    except: return text

# 2. [حل جذري] تعريف القيم الافتراضية في قاموس ثابت
DEFAULTS = {
    'n_w1': 3, 'p_w1': 180000, 'w1_p': 250, 'w1_c': 110, 'w1_d': 12,
    'n_w2': 2, 'p_w2': 320000, 'w2_p': 450, 'w2_c': 180, 'w2_d': 8,
    'n_dr': 3, 'p_dr': 150000, 'd_up': 100, 'd_ec': 15, 'd_ua': 2.0,
    'd_pm': 30, 'sal': 35000, 'f_ex': 10000, 'dep_years': 5
}

# تهيئة الذاكرة إذا كانت فارغة
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.title("🚀 محاكي المغسلة الذكية - النسخة الفولاذية")
st.caption("هذه النسخة تستخدم تقنية الـ Direct Mapping لضمان بقاء البيانات بعد الـ Refresh")

# --- القسم الأول: الأصول (نقرأ ونكتب مباشرة في session_state) ---
with st.expander("🏗️ 1. هيكل الاستثمار والأجهزة", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("**🧺 غسالات 12kg**")
        st.session_state.n_w1 = st.number_input("العدد", min_value=0, value=st.session_state.n_w1, key="nw1_input")
        st.session_state.p_w1 = st.number_input("السعر", min_value=0, value=st.session_state.p_w1, key="pw1_input")
    with c2:
        st.write("**🐘 غسالات 18kg**")
        st.session_state.n_w2 = st.number_input("العدد ", min_value=0, value=st.session_state.n_w2, key="nw2_input")
        st.session_state.p_w2 = st.number_input("السعر ", min_value=0, value=st.session_state.p_w2, key="pw2_input")
    with c3:
        st.write("**🔥 مجففات الغاز**")
        st.session_state.n_dr = st.number_input("العدد  ", min_value=0, value=st.session_state.n_dr, key="ndr_input")
        st.session_state.p_dr = st.number_input("السعر  ", min_value=0, value=st.session_state.p_dr, key="pdr_input")

    st.divider()
    other_inv = st.number_input("مصاريف تأسيس أخرى", value=st.session_state.other_inv, key="oth_input")
    st.session_state.other_inv = other_inv
    
    total_inv = (st.session_state.n_w1 * st.session_state.p_w1) + \
                (st.session_state.n_w2 * st.session_state.p_w2) + \
                (st.session_state.n_dr * st.session_state.p_dr) + st.session_state.other_inv

# --- القسم الثاني: التشغيل ---
st.header("💰 2. التشغيل والأسعار")
o1, o2 = st.columns(2)
with o1:
    st.session_state.w1_p = st.number_input("سعر (12kg)", value=st.session_state.w1_p, key="w1p_in")
    st.session_state.w1_d = st.number_input("زبائن (12kg) يومياً", value=st.session_state.w1_d, key="w1d_in")
    st.session_state.w2_p = st.number_input("سعر (18kg)", value=st.session_state.w2_p, key="w2p_in")
    st.session_state.w2_d = st.number_input("زبائن (18kg) يومياً", value=st.session_state.w2_d, key="w2d_in")

with o2:
    st.session_state.d_up = st.number_input("سعر وحدة التجفيف", value=st.session_state.d_up, key="dup_in")
    st.session_state.sal = st.number_input("الرواتب", value=st.session_state.sal, key="sal_in")
    st.session_state.f_ex = st.number_input("إيجار ومصاريف ثابتة", value=st.session_state.f_ex, key="fex_in")
    st.session_state.d_pm = st.number_input("أيام العمل شهرياً", value=st.session_state.d_pm, key="dpm_in")

# --- الحسابات المالية ---
maint = 20
dry_profit = (st.session_state.d_ua * st.session_state.d_up) - (st.session_state.d_ua * st.session_state.d_ec)
profit_w1 = (st.session_state.w1_p + dry_profit) - (st.session_state.w1_c + maint)
profit_w2 = (st.session_state.w2_p + dry_profit) - (st.session_state.w2_c + maint)

monthly_dep = (total_inv - st.session_state.other_inv) / (max(st.session_state.dep_years, 1) * 12)
monthly_net = ((profit_w1 * st.session_state.w1_d) + (profit_w2 * st.session_state.w2_d)) * st.session_state.d_pm - (st.session_state.sal + st.session_state.f_ex + monthly_dep)

# --- النتائج ---
st.divider()
res1, res2, res3 = st.columns(3)
res1.metric("الربح الصافي الحقيقي", f"{monthly_net:,.0f} دج")
res2.metric("إجمالي الاستثمار", f"{total_inv:,.0f} دج")
res3.metric("فترة الاسترداد", f"{total_inv/monthly_net if monthly_net > 0 else 0:.1f} شهر")

if st.sidebar.button("🗑️ مسح الذاكرة"):
    st.session_state.clear()
    st.rerun()
