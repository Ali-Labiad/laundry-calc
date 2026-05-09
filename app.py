import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro v6.2", layout="wide")

def fix_ar(text):
    try: return get_display(reshape(text))
    except: return text

# 2. [ROOT CAUSE FIX] تعريف القيم الافتراضية في الذاكرة أولاً وقبل كل شيء
# نستخدم قاموساً لضمان وجود القيم حتى لو حدث Refresh
default_values = {
    'w1_p': 250, 'w1_c': 110, 'w1_d': 12,
    'w2_p': 450, 'w2_c': 180, 'w2_d': 8,
    'd_up': 100, 'd_ec': 15, 'd_ua': 2.0, 'd_pm': 30,
    'sal': 35000, 'f_ex': 10000,
    'n_w1': 3, 'p_w1': 180000,
    'n_w2': 2, 'p_w2': 320000,
    'n_dr': 3, 'p_dr': 150000,
    'other_inv': 200000,
    'dep_years': 5
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 3. دالة لتحديث الذاكرة فوراً عند تغيير أي قيمة (Callback)
def update_state():
    for key in default_values.keys():
        if f"input_{key}" in st.session_state:
            st.session_state[key] = st.session_state[f"input_{key}"]

st.title("🚀 محاكي المغسلة الذكية - النسخة المستقرة v6.2")
st.info("💡 تم حل مشكلة الـ Refresh عبر ربط الـ Widgets بنظام المزامنة الفورية.")

# --- القسم الأول: قائمة الأصول ---
with st.expander("🏗️ 1. هيكل الاستثمار (Assets)", expanded=True):
    col_inv1, col_inv2, col_inv3 = st.columns(3)
    
    with col_inv1:
        st.subheader("🧺 غسالات 12kg")
        # الربط المزدوج: نقرأ من الـ session_state ونحدثه عبر الـ key
        n_w1 = st.number_input("عدد الأجهزة", value=st.session_state.n_w1, key="input_n_w1", on_change=update_state)
        p_w1 = st.number_input("السعر (دج)", value=st.session_state.p_w1, key="input_p_w1", on_change=update_state)
        total_w1 = n_w1 * p_w1

    with col_inv2:
        st.subheader("🐘 غسالات 18kg")
        n_w2 = st.number_input("عدد الأجهزة ", value=st.session_state.n_w2, key="input_n_w2", on_change=update_state)
        p_w2 = st.number_input("السعر  (دج)", value=st.session_state.p_w2, key="input_p_w2", on_change=update_state)
        total_w2 = n_w2 * p_w2

    with col_inv3:
        st.subheader("🔥 مجففات الغاز")
        n_dr = st.number_input("عدد المجففات", value=st.session_state.n_dr, key="input_n_dr", on_change=update_state)
        p_dr = st.number_input("سعر المجفف (دج)", value=st.session_state.p_dr, key="input_p_dr", on_change=update_state)
        total_dr = n_dr * p_dr

    st.divider()
    c_inv_a, c_inv_b = st.columns(2)
    other_inv = c_inv_a.number_input("مصاريف التأسيس", value=st.session_state.other_inv, key="input_other_inv", on_change=update_state)
    dep_years = c_inv_b.slider("العمر الافتراضي للأجهزة", 1, 15, value=st.session_state.dep_years, key="input_dep_years", on_change=update_state)
    
    total_investment = total_w1 + total_w2 + total_dr + other_inv
    monthly_depreciation = (total_w1 + total_w2 + total_dr) / (max(dep_years, 1) * 12)

# --- القسم الثاني: التشغيل والأسعار ---
st.header("💰 2. التشغيل والتسعير")
col_opt1, col_opt2 = st.columns(2)

with col_opt1:
    w1_price = st.number_input("سعر غسلة (12kg)", value=st.session_state.w1_p, key="input_w1_p", on_change=update_state)
    w1_daily = st.number_input("زبائن (12kg) يومياً", value=st.session_state.w1_d, key="input_w1_d", on_change=update_state)
    w1_cost = st.number_input("تكلفة المنظفات (12kg)", value=st.session_state.w1_c, key="input_w1_c", on_change=update_state)
    st.write("---")
    w2_price = st.number_input("سعر غسلة (18kg)", value=st.session_state.w2_p, key="input_w2_p", on_change=update_state)
    w2_daily = st.number_input("زبائن (18kg) يومياً", value=st.session_state.w2_d, key="input_w2_d", on_change=update_state)
    w2_cost = st.number_input("تكلفة المنظفات (18kg)", value=st.session_state.w2_c, key="input_w2_c", on_change=update_state)

with col_opt2:
    dryer_unit_price = st.number_input("سعر وحدة التجفيف", value=st.session_state.d_up, key="input_d_up", on_change=update_state)
    dryer_units_avg = st.number_input("وحدات التجفيف/زبون", value=st.session_state.d_ua, key="input_d_ua", on_change=update_state)
    dryer_energy_cost = st.number_input("تكلفة الطاقة/وحدة", value=st.session_state.d_ec, key="input_d_ec", on_change=update_state)
    st.write("---")
    salary = st.number_input("رواتب العمال", value=st.session_state.sal, key="input_sal", on_change=update_state)
    fixed_extra = st.number_input("إيجار ومصاريف ثابتة", value=st.session_state.f_ex, key="input_f_ex", on_change=update_state)
    days_per_month = st.number_input("أيام العمل", value=st.session_state.d_pm, key="input_d_pm", on_change=update_state)

# --- الحسابات (Business Logic) ---
maint_per_cycle = 20
dry_net_per_cust = (dryer_units_avg * dryer_unit_price) - (dryer_units_avg * dryer_energy_cost)
p_w1_single = (w1_price + dry_net_per_cust) - (w1_cost + maint_per_cycle)
p_w2_single = (w2_price + dry_net_per_cust) - (w2_cost + maint_per_cycle)

monthly_gross = ((p_w1_single * w1_daily) + (p_w2_single * w2_daily)) * days_per_month
net_profit_real = monthly_gross - (salary + fixed_extra + monthly_depreciation)

# --- عرض النتائج ---
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("صافي الربح الحقيقي", f"{net_profit_real:,.0f} دج")
k2.metric("فترة الاسترداد", f"{total_investment / net_profit_real if net_profit_real > 0 else 0:.1f} شهر")
k3.metric("مخصص الإهلاك شهرياً", f"{monthly_depreciation:,.0f} دج")
k4.metric("ROI سنوي", f"{(net_profit_real * 12 / total_investment) * 100 if total_investment > 0 else 0:.1f} %")

if st.sidebar.button("🗑️ مسح الذاكرة نهائياً"):
    st.session_state.clear()
    st.rerun()
