import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# إعداد الصفحة
st.set_page_config(page_title="Laundro-Sim Pro", layout="wide")

st.title("🧺 لوحة التحكم المالية للمغسلة الذكية")
st.markdown("---")

# --- القسم الأول: المدخلات الرقمية (بدون Sliders) ---
st.subheader("⚙️ إعدادات التشغيل السريعة")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("💰 استراتيجية البيع")
    # استخدام number_input بدلاً من slider لسهولة التحكم
    wash_price = st.number_input("سعر الغسلة (دج)", min_value=100, max_value=1000, value=250, step=10)
    dryer_units = st.number_input("وحدات التجفيف/زبون", min_value=0.0, max_value=10.0, value=2.0, step=0.5)

with col2:
    st.info("📈 حجم العمل")
    daily_customers = st.number_input("عدد الزبائن يومياً", min_value=1, max_value=200, value=20, step=1)
    days_per_month = st.number_input("أيام العمل/شهر", min_value=1, max_value=31, value=30, step=1)

with col3:
    st.info("🧪 التكاليف المباشرة")
    detergent = st.number_input("منظفات/غسلة (دج)", min_value=0, max_value=500, value=80, step=5)
    energy = st.number_input("طاقة/غسلة (دج)", min_value=0, max_value=500, value=35, step=5)

# --- القسم الثاني: المصاريف الثابتة والاستثمار ---
with st.expander("🏢 المصاريف الثابتة ورأس المال"):
    f_col1, f_col2, f_col3 = st.columns(3)
    salary = f_col1.number_input("الرواتب الشهرية (دج)", value=35000, step=1000)
    fixed_extra = f_col2.number_input("مصاريف أخرى ثابتة", value=10000, step=500)
    investment = f_col3.number_input("إجمالي الاستثمار (دج)", value=1450000, step=50000)

# --- المعادلات الحسابية ---
# تكلفة الصيانة المحتسبة لكل دورة
maint_cost = 20
# صافي ربح الزبون الواحد
profit_per_cust = (wash_price + (dryer_units * 100)) - (detergent + energy + (dryer_units * 15) + maint_cost)
# الربح الصافي الشهري
monthly_net = (profit_per_cust * daily_customers * days_per_month) - (salary + fixed_extra)
# فترة الاسترداد
payback_period = investment / monthly_net if monthly_net > 0 else 0

# --- القسم الثالث: النتائج الرئيسية ---
st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("الربح الصافي (شهري)", f"{monthly_net:,.0f} دج")
m2.metric("فترة الاسترداد", f"{payback_period:.1f} شهر")
m3.metric("نقطة التعادل (زبون/يوم)", f"{(salary + fixed_extra) / (profit_per_cust * days_per_month):.1f}")
m4.metric("ربح الزبون الواحد", f"{profit_per_cust:,.0f} دج")

# --- القسم الرابع: الرسوم البيانية ---
st.divider()
months = np.arange(0, 31) # توقعات لسنتين ونصف
cumulative = (monthly_net * months) - investment

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(months, cumulative, color='#2ecc71' if monthly_net > 0 else '#e74c3c', linewidth=3)
ax.axhline(0, color='black', linestyle='--', alpha=0.5)
ax.set_title("Capital Recovery Timeline")
ax.set_xlabel("Months")
ax.set_ylabel("Net Value (DZD)")
ax.grid(True, alpha=0.2)
st.pyplot(fig)

# رسالة ذكية في الأسفل
if monthly_net > 0:
    st.success(f"✨ التوقعات إيجابية: ستمتلك مشروعاً يدر {monthly_net*12:,.0f} دج سنوياً بعد استرداد رأس المال.")
else:
    st.error("⚠️ النموذج الحالي يظهر خسارة شهرية. يرجى تعديل الأسعار أو تقليل المصاريف.")
