import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro v6", layout="wide")

def fix_ar(text):
    try: return get_display(reshape(text))
    except: return text

# 2. تهيئة الذاكرة (Session State)
if 'w1_p' not in st.session_state:
    defaults = {
        'w1_p': 250, 'w1_c': 110, 'w1_d': 12,
        'w2_p': 450, 'w2_c': 180, 'w2_d': 8,
        'd_up': 100, 'd_ec': 15, 'd_ua': 2.0, 'd_pm': 30,
        'sal': 35000, 'f_ex': 10000,
        'n_w1': 3, 'p_w1': 180000,  # الغسالات المتوسطة
        'n_w2': 2, 'p_w2': 320000,  # الغسالات العملاقة
        'n_dr': 3, 'p_dr': 150000,  # المجففات
        'other_inv': 200000,
        'dep_years': 5 # العمر الافتراضي للأجهزة
    }
    for k, v in defaults.items():
        st.session_state[k] = v

st.title("🚀 محاكي المغسلة الاحترافي - v6")
st.caption("تحليل مالي وتشغيلي دقيق يعتمد على مواصفات الأجهزة الحقيقية")

# --- القسم الأول: تفصيل الأصول والرأسمال ---
with st.expander("🏗️ هيكل الاستثمار وتفاصيل الأصول", expanded=True):
    col_inv1, col_inv2, col_inv3 = st.columns(3)
    
    with col_inv1:
        st.markdown("### 🧺 غسالات متوسطة (12kg)")
        n_w1 = st.number_input("عدد الوحدات", min_value=1, key="n_w1")
        p_w1 = st.number_input("سعر الوحدة (دج)", min_value=0, step=5000, key="p_w1")
        total_w1 = n_w1 * p_w1

    with col_inv2:
        st.markdown("### 🐘 غسالات عملاقة (18kg)")
        n_w2 = st.number_input("عدد الوحدات ", min_value=1, key="n_w2")
        p_w2 = st.number_input("سعر الوحدة  (دج)", min_value=0, step=5000, key="p_w2")
        total_w2 = n_w2 * p_w2

    with col_inv3:
        st.markdown("### 🔥 مجففات الغاز")
        n_dr = st.number_input("عدد الوحدات  ", min_value=1, key="n_dr")
        p_dr = st.number_input("سعر الوحدة   (دج)", min_value=0, step=5000, key="p_dr")
        total_dr = n_dr * p_dr

    st.divider()
    c_inv_a, c_inv_b = st.columns(2)
    other_inv = c_inv_a.number_input("مصاريف التأسيس (ديكور، سباكة، رخص)", min_value=0, key="other_inv")
    dep_years = c_inv_b.slider("العمر الافتراضي للأجهزة (سنوات)", 3, 10, key="dep_years")
    
    investment = total_w1 + total_w2 + total_dr + other_inv
    # حساب الإهلاك الشهري (فقط للأجهزة)
    monthly_depreciation = (total_w1 + total_w2 + total_dr) / (dep_years * 12)

st.markdown("---")

# --- القسم الثاني: التشغيل والأسعار ---
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    st.subheader("💰 استراتيجية التسعير")
    w1_price = st.number_input("سعر خدمة (12kg)", key="w1_p")
    w1_daily = st.number_input("زبائن (12kg) يومياً", key="w1_d")
    w1_cost = st.number_input("تكلفة المنظفات/الدورة (12kg)", key="w1_c")
    st.write("---")
    w2_price = st.number_input("سعر خدمة (18kg)", key="w2_p")
    w2_daily = st.number_input("زبائن (18kg) يومياً", key="w2_d")
    w2_cost = st.number_input("تكلفة المنظفات/الدورة (18kg)", key="w2_c")

with col_opt2:
    st.subheader("📊 النفقات والتشغيل")
    dryer_unit_price = st.number_input("سعر 15 دقيقة تجفيف", key="d_up")
    dryer_units_avg = st.number_input("وحدات التجفيف لكل زبون", key="d_ua")
    dryer_energy_cost = st.number_input("تكلفة الغاز لكل وحدة", key="d_ec")
    st.write("---")
    salary = st.number_input("رواتب العمال شهرياً", key="sal")
    fixed_extra = st.number_input("إيجار ومصاريف ثابتة", key="f_ex")
    days_per_month = st.number_input("أيام التشغيل/شهر", key="d_pm")

# --- العمليات الحسابية ---
maint_per_cycle = 20
dry_net_per_cust = (dryer_units_avg * dryer_unit_price) - (dryer_units_avg * dryer_energy_cost)
profit_w1 = (w1_price + dry_net_per_cust) - (w1_cost + maint_per_cycle)
profit_w2 = (w2_price + dry_net_per_cust) - (w2_cost + maint_per_cycle)

monthly_gross = ((profit_w1 * w1_daily) + (profit_w2 * w2_daily)) * days_per_month
# الربح قبل الإهلاك
ebitda = monthly_gross - (salary + fixed_extra)
# الربح الصافي الحقيقي (بعد خصم الإهلاك)
net_profit_real = ebitda - monthly_depreciation

# حسابات الطاقة الاستيعابية (بافتراض 12 ساعة عمل)
# الدورة الواحدة تأخذ حوالي 45 دقيقة
max_cycles_per_machine = 12
util_w1 = (w1_daily / (n_w1 * max_cycles_per_machine)) * 100
util_w2 = (w2_daily / (n_w2 * max_cycles_per_machine)) * 100

# --- لوحة النتائج ---
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("الربح الصافي الحقيقي", f"{net_profit_real:,.0f} دج", help="بعد خصم الإهلاك وتكاليف التشغيل")
k2.metric("فترة الاسترداد (PBP)", f"{investment / net_profit_real if net_profit_real > 0 else 0:.1f} شهر")
k3.metric("مخصص الإهلاك شهرياً", f"{monthly_depreciation:,.0f} دج", delta_color="inverse")
k4.metric("العائد السنوي (ROI)", f"{(net_profit_real * 12 / investment) * 100 if investment > 0 else 0:.1f} %")

# --- تحليل ذكي للأصول ---
st.subheader("💡 التحليل الاستراتيجي للأصول")
col_an1, col_an2 = st.columns(2)

with col_an1:
    st.write(f"**كفاءة تشغيل الأسطول:**")
    st.write(f"متوسط الربح اليومي من الغسالة الواحدة (12kg): **{profit_w1 * (w1_daily/n_w1) if n_w1 > 0 else 0:,.0f} دج**")
    st.write(f"متوسط الربح اليومي من الغسالة الواحدة (18kg): **{profit_w2 * (w2_daily/n_w2) if n_w2 > 0 else 0:,.0f} دج**")
    
    st.progress(util_w1 / 100 if util_w1 <= 100 else 1.0)
    st.caption(f"نسبة إشغال الغسالات المتوسطة: {util_w1:.1f}%")
    st.progress(util_w2 / 100 if util_w2 <= 100 else 1.0)
    st.caption(f"نسبة إشغال الغسالات العملاقة: {util_w2:.1f}%")

with col_an2:
    if util_w2 > util_w1:
        st.success("🎯 الملاحظة: الغسالات العملاقة تحقق طلباً أعلى. قد يكون من المربح زيادة عددها في التوسعة القادمة.")
    else:
        st.info("ℹ️ الملاحظة: الغسالات المتوسطة هي المحرك الأساسي للعمل حالياً.")
    
    st.warning(f"⚠️ يجب ادخار مبلغ **{monthly_depreciation:,.0f} دج** شهرياً لتجديد الأجهزة بعد **{dep_years}** سنوات.")
