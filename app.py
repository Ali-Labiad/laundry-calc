import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro v4", layout="wide", initial_sidebar_state="collapsed")

# 2. نظام حفظ الحالة (Session State)
# نتحقق من وجود القيم، إذا لم توجد نضع القيم الافتراضية مرة واحدة فقط
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.w1_price = 250
    st.session_state.w1_cost = 110
    st.session_state.w1_daily = 12
    st.session_state.w2_price = 450
    st.session_state.w2_cost = 180
    st.session_state.w2_daily = 8
    st.session_state.dryer_unit_price = 100
    st.session_state.dryer_energy_cost = 15
    st.session_state.dryer_units_avg = 2.0
    st.session_state.days_per_month = 30
    st.session_state.salary = 35000
    st.session_state.fixed_extra = 10000
    st.session_state.investment = 1450000

# دالة لإصلاح اللغة العربية
def fix_ar(text):
    try:
        return get_display(reshape(text))
    except:
        return text

st.title("🚀 محاكي المغسلة الذكية (نظام الذاكرة المستمرة)")
st.caption("سيتم حفظ تعديلاتك تلقائياً خلال هذه الجلسة")

# زر إعادة الضبط في مكان بارز
if st.button("🔄 إعادة ضبط القيم المصنع"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.markdown("---")

# --- واجهة الإدخال المرتبطة بالـ Session State ---
st.subheader("⚙️ إعدادات الفئات (حسب الوزن)")
col1, col2 = st.columns(2)

with col1:
    st.info("🧺 الفئة الأولى (10-12 كغ)")
    # نستخدم on_change لتحديث الـ session_state فوراً
    w1_price = st.number_input("سعر الغسلة (الفئة 1)", min_value=100, value=st.session_state.w1_price, step=10, key="w1_p")
    w1_cost = st.number_input("تكلفة التشغيل (الفئة 1)", min_value=0, value=st.session_state.w1_cost, step=5, key="w1_c")
    w1_daily = st.number_input("الزبائن يومياً (الفئة 1)", min_value=0, value=st.session_state.w1_daily, step=1, key="w1_d")

with col2:
    st.info("🧺 الفئة الثانية (15-18 كغ)")
    w2_price = st.number_input("سعر الغسلة (الفئة 2)", min_value=100, value=st.session_state.w2_price, step=10, key="w2_p")
    w2_cost = st.number_input("تكلفة التشغيل (الفئة 2)", min_value=0, value=st.session_state.w2_cost, step=5, key="w2_c")
    w2_daily = st.number_input("الزبائن يومياً (الفئة 2)", min_value=0, value=st.session_state.w2_daily, step=1, key="w2_d")

st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.info("🔥 إعدادات التجفيف")
    dryer_unit_price = st.number_input("سعر وحدة التجفيف", value=st.session_state.dryer_unit_price, step=10, key="d_up")
    dryer_energy_cost = st.number_input("طاقة التجفيف/وحدة", value=st.session_state.dryer_energy_cost, step=5, key="d_ec")
    # انتبه للـ step هنا (1.0) ليتوافق مع النوع Float
    dryer_units_avg = st.number_input("متوسط الوحدات/زبون", value=st.session_state.dryer_units_avg, step=0.5, key="d_ua")

with col4:
    st.info("📅 التشغيل")
    days_per_month = st.number_input("أيام العمل شهرياً", value=st.session_state.days_per_month, step=1, key="d_pm")
    maint_per_cycle = 20 # قيمة ثابتة أو يمكن جعلها متغيرة

with st.expander("🏢 المصاريف الثابتة ورأس المال"):
    f_col1, f_col2, f_col3 = st.columns(3)
    salary = f_col1.number_input("الرواتب الشهرية", value=st.session_state.salary, step=1000, key="sal")
    fixed_extra = f_col2.number_input("مصاريف أخرى", value=st.session_state.fixed_extra, step=500, key="f_ex")
    investment = f_col3.number_input("الاستثمار الأولي", value=st.session_state.investment, step=50000, key="inv")

# --- تحديث الذاكرة بالقيم الجديدة قبل الحسابات ---
st.session_state.w1_price = w1_price
st.session_state.w1_cost = w1_cost
st.session_state.w1_daily = w1_daily
st.session_state.w2_price = w2_price
st.session_state.w2_cost = w2_cost
st.session_state.w2_daily = w2_daily
st.session_state.dryer_unit_price = dryer_unit_price
st.session_state.dryer_energy_cost = dryer_energy_cost
st.session_state.dryer_units_avg = dryer_units_avg
st.session_state.days_per_month = days_per_month
st.session_state.salary = salary
st.session_state.fixed_extra = fixed_extra
st.session_state.investment = investment

# --- الحسابات المنطقية ---
dry_net_per_cust = (dryer_units_avg * dryer_unit_price) - (dryer_units_avg * dryer_energy_cost)
profit_w1 = (w1_price + dry_net_per_cust) - (w1_cost + maint_per_cycle)
profit_w2 = (w2_price + dry_net_per_cust) - (w2_cost + maint_per_cycle)

monthly_gross_profit = ( (profit_w1 * w1_daily) + (profit_w2 * w2_daily) ) * days_per_month
monthly_net = monthly_gross_profit - (salary + fixed_extra)

payback_months = investment / monthly_net if monthly_net > 0 else 0
roi_annual = (monthly_net * 12 / investment) * 100 if investment > 0 else 0
total_daily_cust = w1_daily + w2_daily
avg_profit_per_cust = ( (profit_w1 * w1_daily) + (profit_w2 * w2_daily) ) / total_daily_cust if total_daily_cust > 0 else 0
break_even_daily = (salary + fixed_extra) / (avg_profit_per_cust * days_per_month) if avg_profit_per_cust > 0 else 0

# --- العرض ---
st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("الربح الصافي (شهري)", f"{monthly_net:,.0f} دج")
m2.metric("فترة الاسترداد", f"{payback_months:.1f} شهر")
m3.metric("نقطة التعادل", f"{break_even_daily:.1f} زبون/يوم")
m4.metric("ROI سنوي", f"{roi_annual:.1f} %")

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
    st.table(pd.DataFrame({
        "الفئة": [fix_ar("الصغيرة"), fix_ar("الكبيرة")],
        "صافي الربح/زبون": [f"{profit_w1:,.0f}", f"{profit_w2:,.0f}"],
        "المساهمة الشهرية": [f"{profit_w1 * w1_daily * days_per_month:,.0f}", f"{profit_w2 * w2_daily * days_per_month:,.0f}"]
    }))

if st.button("📝 توليد التقرير النهائي"):
    st.code(f"الربح: {monthly_net:,.0f} دج | الاسترداد: {payback_months:.1f} شهر")
