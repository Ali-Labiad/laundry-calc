import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro v4", layout="wide")

# دالة لإصلاح اللغة العربية
def fix_ar(text):
    try:
        return get_display(reshape(text))
    except:
        return text

# 2. تهيئة الذاكرة (تنفذ فقط عند أول زيارة للموقع)
# نستخدم هذا البلوك لضمان وجود مفاتيح الذاكرة قبل رسم أي Widget
if 'w1_p' not in st.session_state:
    # الفئة 1
    st.session_state['w1_p'] = 250
    st.session_state['w1_c'] = 110
    st.session_state['w1_d'] = 12
    # الفئة 2
    st.session_state['w2_p'] = 450
    st.session_state['w2_c'] = 180
    st.session_state['w2_d'] = 8
    # التجفيف والتشغيل
    st.session_state['d_up'] = 100
    st.session_state['d_ec'] = 15
    st.session_state['d_ua'] = 2.0
    st.session_state['d_pm'] = 30
    # الثوابت والاستثمار
    st.session_state['sal'] = 35000
    st.session_state['f_ex'] = 10000
    st.session_state['inv'] = 1450000

st.title("🚀 محاكي المغسلة الذكية (النسخة المستقرة)")
st.caption("هذه النسخة تحفظ المعطيات تلقائياً في ذاكرة المتصفح")

# زر إعادة الضبط
if st.button("🔄 إعادة ضبط القيم الأصلية"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.markdown("---")

# --- واجهة الإدخال ---
# ملاحظة هامة: لا نستخدم (value=) هنا، بل نعتمد كلياً على (key=)
st.subheader("⚙️ إعدادات الفئات (حسب الوزن)")
col1, col2 = st.columns(2)

with col1:
    st.info("🧺 الفئة الأولى (10-12 كغ)")
    w1_price = st.number_input("سعر الغسلة (الفئة 1)", min_value=100, step=10, key="w1_p")
    w1_cost = st.number_input("تكلفة التشغيل (الفئة 1)", min_value=0, step=5, key="w1_c")
    w1_daily = st.number_input("الزبائن يومياً (الفئة 1)", min_value=0, step=1, key="w1_d")

with col2:
    st.info("🧺 الفئة الثانية (15-18 كغ)")
    w2_price = st.number_input("سعر الغسلة (الفئة 2)", min_value=100, step=10, key="w2_p")
    w2_cost = st.number_input("تكلفة التشغيل (الفئة 2)", min_value=0, step=5, key="w2_c")
    w2_daily = st.number_input("الزبائن يومياً (الفئة 2)", min_value=0, step=1, key="w2_d")

st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.info("🔥 إعدادات التجفيف")
    dryer_unit_price = st.number_input("سعر وحدة التجفيف", step=10, key="d_up")
    dryer_energy_cost = st.number_input("طاقة التجفيف/وحدة", step=5, key="d_ec")
    dryer_units_avg = st.number_input("متوسط الوحدات/زبون", step=0.5, key="d_ua")

with col4:
    st.info("📅 التشغيل")
    days_per_month = st.number_input("أيام العمل شهرياً", step=1, key="d_pm")
    maint_per_cycle = 20 

with st.expander("🏢 المصاريف الثابتة ورأس المال"):
    f_col1, f_col2, f_col3 = st.columns(3)
    salary = f_col1.number_input("الرواتب الشهرية", step=1000, key="sal")
    fixed_extra = f_col2.number_input("مصاريف أخرى", step=500, key="f_ex")
    investment = f_col3.number_input("الاستثمار الأولي", step=50000, key="inv")

# --- الحسابات المالية (تستخدم القيم الحالية من الخانات) ---
dry_net_per_cust = (dryer_units_avg * dryer_unit_price) - (dryer_units_avg * dryer_energy_cost)
profit_w1 = (w1_price + dry_net_per_cust) - (w1_cost + maint_per_cycle)
profit_w2 = (w2_price + dry_net_per_cust) - (w2_cost + maint_per_cycle)

monthly_gross_profit = ( (profit_w1 * w1_daily) + (profit_w2 * w2_daily) ) * days_per_month
monthly_net = monthly_gross_profit - (salary + fixed_extra)

# الحماية من القسمة على صفر
payback_months = investment / monthly_net if monthly_net > 0 else 0
roi_annual = (monthly_net * 12 / investment) * 100 if investment > 0 else 0
total_daily_cust = w1_daily + w2_daily
avg_profit_per_cust = ( (profit_w1 * w1_daily) + (profit_w2 * w2_daily) ) / total_daily_cust if total_daily_cust > 0 else 0
break_even_daily = (salary + fixed_extra) / (avg_profit_per_cust * days_per_month) if avg_profit_per_cust > 0 and days_per_month > 0 else 0

# --- النتائج ---
st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("الربح الصافي (شهري)", f"{monthly_net:,.0f} دج")
m2.metric("فترة الاسترداد", f"{payback_months:.1f} شهر")
m3.metric("نقطة التعادل", f"{break_even_daily:.1f} زبون/يوم")
m4.metric("ROI سنوي", f"{roi_annual:.1f} %")

# --- الرسوم البيانية ---
tab1, tab2 = st.tabs(["📉 تحليل النمو", "📊 المقارنة"])
with tab1:
    months = np.arange(0, 31)
    cumulative = (monthly_net * months) - investment
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(months, cumulative, color='#2ecc71' if monthly_net > 0 else '#e74c3c', linewidth=3)
    ax.axhline(0, color='black', linestyle='--', alpha=0.3)
    ax.set_title(fix_ar("مسار استرداد رأس المال"))
    st.pyplot(fig)

with tab2:
    comparison_df = pd.DataFrame({
        "الفئة": [fix_ar("الصغيرة"), fix_ar("الكبيرة")],
        "صافي الربح/زبون": [f"{profit_w1:,.0f}", f"{profit_w2:,.0f}"],
        "المساهمة الشهرية": [f"{profit_w1 * w1_daily * days_per_month:,.0f}", f"{profit_w2 * w2_daily * days_per_month:,.0f}"]
    })
    st.table(comparison_df)
