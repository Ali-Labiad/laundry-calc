import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro v5", layout="wide")

def fix_ar(text):
    try: return get_display(reshape(text))
    except: return text

# 2. تهيئة الذاكرة (Session State)
if 'w1_p' not in st.session_state:
    # الفئات والتشغيل
    defaults = {
        'w1_p': 250, 'w1_c': 110, 'w1_d': 12,
        'w2_p': 450, 'w2_c': 180, 'w2_d': 8,
        'd_up': 100, 'd_ec': 15, 'd_ua': 2.0, 'd_pm': 30,
        'sal': 35000, 'f_ex': 10000,
        # تفاصيل الاستثمار الجديد
        'n_w1': 3, 'p_w1': 180000,  # عدد وسعر غسالات ف1
        'n_w2': 2, 'p_w2': 320000,  # عدد وسعر غسالات ف2
        'n_dr': 3, 'p_dr': 150000,  # عدد وسعر المجففات
        'other_inv': 200000         # ديكور، رخص، ومصاريف أخرى
    }
    for k, v in defaults.items():
        st.session_state[k] = v

st.title("🚀 محاكي المغسلة الذكية - الإصدار الإستراتيجي v5")

# --- واجهة الإدخال ---
with st.expander("🏗️ تفاصيل الاستثمار الأولي (قائمة الأجهزة)", expanded=True):
    col_inv1, col_inv2, col_inv3 = st.columns(3)
    
    with col_inv1:
        st.write("**غسالات الفئة 1**")
        n_w1 = st.number_input("عدد الأجهزة (ف1)", min_value=1, key="n_w1")
        p_w1 = st.number_input("سعر الجهاز الواحد (ف1)", min_value=0, step=5000, key="p_w1")
        total_w1 = n_w1 * p_w1
        st.caption(f"إجمالي الفئة 1: {total_w1:,.0f} دج")

    with col_inv2:
        st.write("**غسالات الفئة 2**")
        n_w2 = st.number_input("عدد الأجهزة (ف2)", min_value=1, key="n_w2")
        p_w2 = st.number_input("سعر الجهاز الواحد (ف2)", min_value=0, step=5000, key="p_w2")
        total_w2 = n_w2 * p_w2
        st.caption(f"إجمالي الفئة 2: {total_w2:,.0f} دج")

    with col_inv3:
        st.write("**المجففات (Dryers)**")
        n_dr = st.number_input("عدد المجففات", min_value=1, key="n_dr")
        p_dr = st.number_input("سعر المجفف الواحد", min_value=0, step=5000, key="p_dr")
        total_dr = n_dr * p_dr
        st.caption(f"إجمالي المجففات: {total_dr:,.0f} دج")

    other_inv = st.number_input("مصاريف تأسيس أخرى (ديكور، رخص، سباكة...)", min_value=0, key="other_inv")
    
    investment = total_w1 + total_w2 + total_dr + other_inv
    st.info(f"💰 إجمالي الاستثمار المحسوب: {investment:,.0f} دج")

st.markdown("---")

# --- باقي المدخلات (الفئات والتشغيل) ---
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    st.subheader("⚙️ أسعار الخدمات والإقبال")
    w1_price = st.number_input("سعر الغسلة (ف1)", key="w1_p")
    w1_daily = st.number_input("الزبائن يومياً (ف1)", key="w1_d")
    w1_cost = st.number_input("تكلفة التشغيل (ف1)", key="w1_c")
    st.write("---")
    w2_price = st.number_input("سعر الغسلة (ف2)", key="w2_p")
    w2_daily = st.number_input("الزبائن يومياً (ف2)", key="w2_d")
    w2_cost = st.number_input("تكلفة التشغيل (ف2)", key="w2_c")

with col_opt2:
    st.subheader("🔥 التجفيف والمصاريف")
    dryer_unit_price = st.number_input("سعر وحدة التجفيف", key="d_up")
    dryer_units_avg = st.number_input("وحدات التجفيف/زبون", key="d_ua")
    dryer_energy_cost = st.number_input("تكلفة الطاقة/وحدة", key="d_ec")
    st.write("---")
    salary = st.number_input("الرواتب الشهرية", key="sal")
    fixed_extra = st.number_input("مصاريف ثابتة أخرى", key="f_ex")
    days_per_month = st.number_input("أيام العمل", key="d_pm")

# --- الحسابات المالية ---
maint_per_cycle = 20
dry_net_per_cust = (dryer_units_avg * dryer_unit_price) - (dryer_units_avg * dryer_energy_cost)
profit_w1 = (w1_price + dry_net_per_cust) - (w1_cost + maint_per_cycle)
profit_w2 = (w2_price + dry_net_per_cust) - (w2_cost + maint_per_cycle)

monthly_gross_profit = ((profit_w1 * w1_daily) + (profit_w2 * w2_daily)) * days_per_month
monthly_net = monthly_gross_profit - (salary + fixed_extra)

# --- تحليل الطاقة الاستيعابية (الاستخدام الجديد لعدد الأجهزة) ---
# نفترض أن الجهاز الواحد يمكنه العمل 10 دورات في اليوم كحد أقصى
capacity_w1 = n_w1 * 10
capacity_w2 = n_w2 * 10
utilization_w1 = (w1_daily / capacity_w1) * 100 if capacity_w1 > 0 else 0
utilization_w2 = (w2_daily / capacity_w2) * 100 if capacity_w2 > 0 else 0

# --- النتائج ---
st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("الربح الصافي (شهري)", f"{monthly_net:,.0f} دج")
m2.metric("فترة الاسترداد", f"{investment / monthly_net if monthly_net > 0 else 0:.1f} شهر")
m3.metric("ROI سنوي", f"{(monthly_net * 12 / investment) * 100 if investment > 0 else 0:.1f} %")
m4.metric("إجمالي الاستثمار", f"{investment:,.0f} دج")

# --- تحليل الطاقة الاستيعابية ---
st.subheader("📊 تحليل استخدام الأجهزة (Capacity Analysis)")
c_col1, c_col2 = st.columns(2)
c_col1.progress(utilization_w1 / 100 if utilization_w1 <= 100 else 1.0)
c_col1.write(f"نسبة إشغال غسالات ف1: {utilization_w1:.1f}%")
c_col2.progress(utilization_w2 / 100 if utilization_w2 <= 100 else 1.0)
c_col2.write(f"نسبة إشغال غسالات ف2: {utilization_w2:.1f}%")

if utilization_w1 > 90 or utilization_w2 > 90:
    st.warning("⚠️ تنبيه: لقد اقتربت من أقصى طاقة استيعابية للأجهزة. فكر في زيادة عدد الأجهزة إذا زاد الطلب.")
