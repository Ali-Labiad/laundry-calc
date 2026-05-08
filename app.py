import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# إعداد واجهة التطبيق لتناسب الهاتف
st.set_page_config(page_title="Laundro-Sim", layout="centered")

st.title("📊 محاكي مشروع المغسلة")
st.write("قم بتعديل القيم لمشاهدة الأرباح اللحظية")

# --- مدخلات المشروع ---
with st.expander("💰 إعدادات التسعير والزبائن", expanded=True):
    wash_price = st.slider("سعر الغسلة (دج)", 200, 500, 250)
    daily_customers = st.slider("عدد الزبائن يومياً", 1, 60, 20)
    dryer_units = st.number_input("وحدات التجفيف/زبون (12د للوحدة)", 0.0, 5.0, 2.0)

with st.expander("🧪 التكاليف المتغيرة (لكل دورة)"):
    detergent = st.number_input("منظفات ومعطرات (دج)", 30, 150, 80)
    energy = st.number_input("طاقة (غاز/ماء/كهرباء)", 10, 100, 35)
    maintenance = st.number_input("صندوق صيانة دوري", 5, 50, 20)

with st.expander("🏢 المصاريف الثابتة والاستثمار"):
    salary = st.number_input("رواتب العمال شهرياً", 0, 150000, 35000)
    fixed_extra = st.number_input("مصاريف ثابتة أخرى", 0, 50000, 10000)
    investment = st.number_input("إجمالي الاستثمار الأولي", 1000000, 3000000, 1450000)

# --- المعادلات الحسابية ---
# تكلفة التجفيف (نعتبر 15 دج للوحدة الواحدة طاقة)
dryer_revenue = dryer_units * 100
dryer_cost = dryer_units * 15

profit_per_cust = (wash_price + dryer_revenue) - (detergent + energy + maintenance + dryer_cost)
monthly_profit = (profit_per_cust * daily_customers * 30) - (salary + fixed_extra)
payback_period = investment / monthly_profit if monthly_profit > 0 else 0

# --- عرض النتائج ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.metric("الربح الصافي (شهري)", f"{monthly_profit:,.0f} دج")
with c2:
    st.metric("فترة الاسترداد", f"{payback_period:.1f} شهر")

# جدول زمني للأرباح
st.subheader("🗓️ التوقعات الزمنية")
time_data = {
    "الفترة": ["شهر", "سنة", "سنتين"],
    "الربح الصافي (دج)": [
        f"{monthly_profit:,.0f}",
        f"{monthly_profit * 12:,.0f}",
        f"{monthly_profit * 24:,.0f}"
    ]
}
st.table(pd.DataFrame(time_data))

# رسم بياني بسيط لنقطة التعادل
months = np.arange(0, 25)
cumulative = (monthly_profit * months) - investment
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(months, cumulative, color='#2ecc71', linewidth=3)
ax.axhline(0, color='#e74c3c', linestyle='--')
ax.set_title("مسار استرداد رأس المال")
ax.set_xlabel("الأشهر")
ax.set_ylabel("دج")
st.pyplot(fig)
