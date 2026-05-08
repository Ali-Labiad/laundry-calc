import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# إعدادات الصفحة والتصميم
st.set_page_config(page_title="Laundro-Sim Pro v4", layout="wide", initial_sidebar_state="collapsed")

# دالة لإصلاح اللغة العربية في الرسوم البيانية
def fix_ar(text):
    try:
        return get_display(reshape(text))
    except:
        return text

st.title("🚀 محاكي القرار الاستراتيجي - المغسلة الذكية (نظام الفئات)")
st.markdown("---")

# --- واجهة الإدخال العملية (تم تقسيمها حسب نوع الغسالات) ---
st.subheader("⚙️ إعدادات الفئات (حسب الوزن)")
col1, col2 = st.columns(2)

with col1:
    st.info("🧺 الفئة الأولى (مثلاً 10-12 كغ)")
    w1_price = st.number_input("سعر الغسلة (الفئة 1)", min_value=100, value=250, step=10)
    w1_cost = st.number_input("تكلفة المنظفات+الطاقة (الفئة 1)", min_value=0, value=110, step=5)
    w1_daily = st.number_input("عدد الزبائن يومياً (الفئة 1)", min_value=0, value=12, step=1)

with col2:
    st.info("🧺 الفئة الثانية (مثلاً 15-18 كغ)")
    w2_price = st.number_input("سعر الغسلة (الفئة 2)", min_value=100, value=450, step=10)
    w2_cost = st.number_input("تكلفة المنظفات+الطاقة (الفئة 2)", min_value=0, value=180, step=5)
    w2_daily = st.number_input("عدد الزبائن يومياً (الفئة 2)", min_value=0, value=8, step=1)

st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.info("🔥 إعدادات التجفيف")
    dryer_unit_price = st.number_input("سعر وحدة التجفيف (12د)", min_value=0, value=100, step=10)
    dryer_energy_cost = st.number_input("تكلفة طاقة التجفيف/وحدة", min_value=0, value=15, step=5)
    dryer_units_avg = st.number_input("متوسط وحدات التجفيف لكل زبون", min_value=0.0, value=2.0, step=0.5)

with col4:
    st.info("📅 التشغيل")
    days_per_month = st.number_input("أيام العمل في الشهر", min_value=1, max_value=31, value=30, step=1)
    maint_per_cycle = st.number_input("صندوق الصيانة (دج/دورة)", value=20)

with st.expander("🏢 المصاريف الثابتة ورأس المال"):
    f_col1, f_col2, f_col3 = st.columns(3)
    salary = f_col1.number_input("إجمالي الرواتب الشهرية", value=35000, step=1000)
    fixed_extra = f_col2.number_input("مصاريف ثابتة أخرى", value=10000, step=500)
    investment = f_col3.number_input("إجمالي الاستثمار الأولي", value=1450000, step=50000)

# --- المعادلات الحسابية المتقدمة (نظام الفئات) ---
# حساب ربح التجفيف الصافي لكل زبون
dry_net_per_cust = (dryer_units_avg * dryer_unit_price) - (dryer_units_avg * dryer_energy_cost)

# حساب صافي ربح الزبون في كل فئة
profit_w1 = (w1_price + dry_net_per_cust) - (w1_cost + maint_per_cycle)
profit_w2 = (w2_price + dry_net_per_cust) - (w2_cost + maint_per_cycle)

# الأرباح الشهرية
monthly_gross_profit = ( (profit_w1 * w1_daily) + (profit_w2 * w2_daily) ) * days_per_month
monthly_net = monthly_gross_profit - (salary + fixed_extra)

# المقاييس المالية
payback_months = investment / monthly_net if monthly_net > 0 else 0
roi_annual = (monthly_net * 12 / investment) * 100 if investment > 0 else 0
total_daily_cust = w1_daily + w2_daily
avg_profit_per_cust = ( (profit_w1 * w1_daily) + (profit_w2 * w2_daily) ) / total_daily_cust if total_daily_cust > 0 else 0
break_even_daily = (salary + fixed_extra) / (avg_profit_per_cust * days_per_month) if avg_profit_per_cust > 0 else 0

# --- عرض النتائج الاستراتيجية ---
st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("الربح الصافي (شهري)", f"{monthly_net:,.0f} دج")
m2.metric("فترة الاسترداد", f"{payback_months:.1f} شهر")
m3.metric("نقطة التعادل الإجمالية", f"{break_even_daily:.1f} زبون/يوم")
m4.metric("العائد السنوي ROI", f"{roi_annual:.1f} %")

# --- التحليل البياني ---
st.divider()
tab1, tab2 = st.tabs(["📉 مسار الأرباح التراكمي", "📊 مقارنة الفئات"])

with tab1:
    months = np.arange(0, 31)
    cumulative = (monthly_net * months) - investment
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(months, cumulative, color='#2ecc71' if monthly_net > 0 else '#e74c3c', linewidth=3)
    ax.axhline(0, color='black', linestyle='--', alpha=0.3)
    ax.set_title(fix_ar("توقعات استرداد رأس المال (30 شهر)"))
    ax.set_xlabel(fix_ar("الأشهر"))
    ax.set_ylabel(fix_ar("القيمة التراكمية (دج)"))
    ax.grid(True, alpha=0.1)
    st.pyplot(fig)

with tab2:
    # عرض جدول مقارنة الفئات
    comparison_data = {
        "الفئة": [fix_ar("الصغيرة"), fix_ar("الكبيرة")],
        "صافي ربح الزبون (دج)": [f"{profit_w1:,.0f}", f"{profit_w2:,.0f}"],
        "المساهمة الشهرية": [f"{profit_w1 * w1_daily * days_per_month:,.0f}", f"{profit_w2 * w2_daily * days_per_month:,.0f}"]
    }
    st.table(pd.DataFrame(comparison_data))

# --- رسائل دعم القرار ---
if monthly_net <= 0:
    st.error("⚠️ تحذير: النموذج الحالي خاسر. راجع توزيع الإقبال أو ارفع الأسعار.")
else:
    st.success(f"✨ المشروع يدر أرباحاً جيدة. الفئة الكبيرة تساهم بـ {((profit_w2 * w2_daily * days_per_month)/monthly_gross_profit)*100:.1f}% من إجمالي دخل العمليات.")

if st.button("📝 ملخص التقرير النهائي"):
    st.code(f"""
    تقرير المحاكاة المتقدمة:
    --------------------------
    - الربح الشهري الصافي: {monthly_net:,.0f} دج
    - فترة الاسترداد: {payback_months:.1f} شهر
    - ربح الفئة 1 (للزائر): {profit_w1:,.0f} دج
    - ربح الفئة 2 (للزائر): {profit_w2:,.0f} دج
    - هدف الزبائن اليومي الكلي: {break_even_daily:.1f} زبون
    --------------------------
    طُبع بتاريخ: 2026-05-08
    """)
