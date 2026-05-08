import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# إعدادات الصفحة والتصميم
st.set_page_config(page_title="Laundro-Sim Pro", layout="wide", initial_sidebar_state="collapsed")

# دالة لإصلاح اللغة العربية في الرسوم البيانية
def fix_ar(text):
    try:
        return get_display(reshape(text))
    except:
        return text

st.title("🚀 محاكي القرار الاستراتيجي - المغسلة الذكية")
st.markdown("---")

# --- واجهة الإدخال العملية (بدون Sliders) ---
st.subheader("⚙️ إعدادات النموذج المالي")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("💰 استراتيجية البيع")
    wash_price = st.number_input("سعر الغسلة (دج)", min_value=100, value=250, step=10)
    dryer_unit_price = st.number_input("سعر وحدة التجفيف (12د)", min_value=0, value=100, step=5)
    dryer_units = st.number_input("متوسط وحدات التجفيف/زبون", min_value=0, value=2, step=1)

with col2:
    st.info("📈 حجم الإقبال والعمل")
    daily_customers = st.number_input("عدد الزبائن يومياً", min_value=1, value=20, step=1)
    days_per_month = st.number_input("أيام العمل في الشهر", min_value=1, max_value=31, value=30, step=1)

with col3:
    st.info("🧪 تكاليف التشغيل المباشرة")
    detergent = st.number_input("المنظفات (دج/دورة)", min_value=0, value=80, step=5)
    energy_wash = st.number_input("طاقة الغسيل (دج/دورة)", min_value=0, value=35, step=5)
    energy_dry = st.number_input("طاقة التجفيف (دج/وحدة)", min_value=0, value=15, step=5)

with st.expander("🏢 المصاريف الثابتة ورأس المال"):
    f_col1, f_col2, f_col3 = st.columns(3)
    salary = f_col1.number_input("إجمالي الرواتب الشهرية", value=35000, step=1000)
    fixed_extra = f_col2.number_input("مصاريف ثابتة أخرى", value=10000, step=500)
    investment = f_col3.number_input("إجمالي الاستثمار الأولي", value=1450000, step=50000)

# --- المعادلات الحسابية المتقدمة ---
maint_per_cycle = 20
revenue_per_cust = wash_price + (dryer_units * dryer_unit_price)
cost_per_cust = detergent + energy_wash + (dryer_units * energy_dry) + maint_per_cycle
profit_per_cust = revenue_per_cust - cost_per_cust

monthly_revenue = revenue_per_cust * daily_customers * days_per_month
monthly_expenses = (cost_per_cust * daily_customers * days_per_month) + salary + fixed_extra
monthly_net = monthly_revenue - monthly_expenses

payback_months = investment / monthly_net if monthly_net > 0 else 0
roi_annual = (monthly_net * 12 / investment) * 100 if investment > 0 else 0
break_even_cust = (salary + fixed_extra) / (profit_per_cust * days_per_month) if profit_per_cust > 0 else 0

# --- عرض النتائج الاستراتيجية ---
st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("الربح الصافي (شهري)", f"{monthly_net:,.0f} دج")
m2.metric("فترة الاسترداد", f"{payback_months:.1f} شهر")
m3.metric("نقطة التعادل (زبون/يوم)", f"{break_even_cust:.1f}")
m4.metric("العائد السنوي ROI", f"{roi_annual:.1f} %")

# --- التحليل البياني ---
st.divider()
tab1, tab2 = st.tabs(["📉 مسار الأرباح", "📊 هيكل التكاليف"])

with tab1:
    months = np.arange(0, 31)
    cumulative = (monthly_net * months) - investment
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(months, cumulative, color='#2ecc71' if monthly_net > 0 else '#e74c3c', linewidth=3)
    ax.axhline(0, color='black', linestyle='--', alpha=0.3)
    
    # حل مشكلة اللغة العربية في العناوين
    ax.set_title(fix_ar("توقعات استرداد رأس المال (30 شهر)"))
    ax.set_xlabel(fix_ar("الأشهر"))
    ax.set_ylabel(fix_ar("القيمة التراكمية (دج)"))
    ax.grid(True, alpha=0.1)
    st.pyplot(fig)

with tab2:
    # مقارنة الدخل والمصاريف
    st.write(f"**إجمالي الدخل الشهري:** {monthly_revenue:,.0f} دج")
    st.write(f"**إجمالي المصاريف الشهرية:** {monthly_expenses:,.0f} دج")
    st.progress(min(max(monthly_expenses/monthly_revenue, 0.0), 1.0) if monthly_revenue > 0 else 0)
    st.caption("نسبة المصاريف من إجمالي الدخل")

# --- رسائل دعم القرار (Logic Engine) ---
if monthly_net <= 0:
    st.error("⚠️ تحذير: النموذج الحالي يظهر خسارة. زد السعر أو قلل الرواتب.")
elif payback_months > 18:
    st.warning(f"ℹ️ تنبيه: فترة الاسترداد ({payback_months:.1f} شهر) تعتبر طويلة نسبياً لهذا النوع من المشاريع.")
else:
    st.success("✨ مؤشرات ممتازة: المشروع يظهر كفاءة عالية في استرداد رأس المال.")

# إضافة خاصية التصدير (نصية حالياً لسهولة النسخ)
if st.button("📝 توليد ملخص التقرير للنسخ"):
    report = f"""
    تقرير مشروع المغسلة الذكية:
    --------------------------
    - سعر الغسلة: {wash_price} دج
    - الربح الصافي الشهري المتوقع: {monthly_net:,.0f} دج
    - فترة استرداد رأس المال: {payback_months:.1f} شهر
    - نقطة التعادل: {break_even_cust:.1f} زبون يومياً
    --------------------------
    طُبع بتاريخ: 2026-05-07
    """
    st.code(report)
