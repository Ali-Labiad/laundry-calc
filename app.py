import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Laundro-Sim Pro", layout="wide")

# دالة لتحسين المظهر الجمالي للرسوم البيانية
plt.style.use('ggplot')

st.title("🚀 محاكي القرار الاستراتيجي - المغسلة الذكية")
st.markdown("---")

# --- القائمة الجانبية (Sidebar) للتحكم المتقدم ---
st.sidebar.header("🛠️ إعدادات النموذج")

with st.sidebar.expander("💰 الأسعار والزبائن"):
    wash_price = st.slider("سعر الغسلة (دج)", 200, 500, 250)
    daily_customers = st.slider("عدد الزبائن (الحالة المتوقعة)", 1, 60, 20)
    occupancy_rate = st.slider("نسبة الإشغال (%)", 50, 100, 100) / 100
    dryer_units = st.number_input("وحدات التجفيف لكل زبون", 0.0, 5.0, 2.0)

with st.sidebar.expander("🧪 تكاليف التشغيل"):
    detergent = st.number_input("المنظفات (دج/دورة)", 30, 150, 80)
    energy = st.number_input("طاقة/ماء (دج/دورة)", 10, 100, 35)
    salary = st.number_input("رواتب العمال (شهري)", 0, 150000, 35000)
    fixed_extra = st.number_input("مصاريف أخرى ثابتة", 0, 50000, 10000)
    investment = st.number_input("إجمالي الاستثمار", 1000000, 3000000, 1450000)

# --- الحسابات المنطقية المتقدمة ---
actual_daily_cust = daily_customers * occupancy_rate
dryer_revenue = dryer_units * 100
dryer_cost = dryer_units * 15 # تكلفة الغاز/كهرباء للوحدة

# هامش الربح للزبون الواحد
profit_per_cust = (wash_price + dryer_revenue) - (detergent + energy + dryer_cost + 20) # 20دج صيانة
monthly_rev = (wash_price + dryer_revenue) * actual_daily_cust * 30
monthly_exp = (detergent + energy + dryer_cost + 20) * actual_daily_cust * 30 + salary + fixed_extra
monthly_net = monthly_rev - monthly_exp

# نقطة التعادل (Break-even Point in Customers)
break_even_cust = (salary + fixed_extra) / (profit_per_cust * 30) if profit_per_cust > 0 else 0
payback_period = investment / monthly_net if monthly_net > 0 else 0
roi_annual = (monthly_net * 12 / investment) * 100 if investment > 0 else 0

# --- عرض النتائج الاحترافية (Metrics) ---
cols = st.columns(4)
cols[0].metric("الربح الصافي (شهري)", f"{monthly_net:,.0f} دج")
cols[1].metric("فترة الاسترداد", f"{payback_period:.1f} شهر")
cols[2].metric("نقطة التعادل", f"{break_even_cust:.1f} زبون/يوم")
cols[3].metric("العائد السنوي (ROI)", f"{roi_annual:.1f} %")

st.markdown("---")

# --- تحليل السيناريوهات (Charts) ---
st.subheader("📊 تحليل المسار المالي")

tab1, tab2 = st.tabs(["📉 مسار الأرباح", "📊 تحليل الحساسية (السعر)"])

with tab1:
    months = np.arange(0, 37) # 3 سنوات
    cumulative = (monthly_net * months) - investment
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(months, cumulative, color='#3498db', linewidth=3, label="Current Scenario")
    ax.axhline(0, color='#e74c3c', linestyle='--')
    ax.fill_between(months, cumulative, 0, where=(cumulative > 0), facecolor='green', alpha=0.1)
    ax.fill_between(months, cumulative, 0, where=(cumulative < 0), facecolor='red', alpha=0.1)
    ax.set_title("Capital Recovery Path (3 Years Projection)")
    ax.set_xlabel("Months")
    ax.set_ylabel("Net Position (DZD)")
    st.pyplot(fig)

with tab2:
    # مقارنة أسعار مختلفة
    prices = [250, 300, 350, 400]
    monthly_profits = [( ( (p + dryer_revenue) - (detergent + energy + dryer_cost + 20) ) * actual_daily_cust * 30 ) - (salary + fixed_extra) for p in prices]
    
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    bars = ax2.bar([str(p) for p in prices], monthly_profits, color='#9b59b6')
    ax2.set_title("Monthly Profit vs. Washing Price")
    ax2.set_ylabel("Monthly Net Profit (DZD)")
    ax2.set_xlabel("Washing Price (DZD)")
    st.pyplot(fig2)

# --- رسالة تنبيه ذكية ---
if actual_daily_cust < break_even_cust:
    st.error(f"⚠️ تحذير: عدد الزبائن الحالي ({actual_daily_cust:.1f}) أقل من نقطة التعادل ({break_even_cust:.1f}). أنت تخسر مالاً!")
elif payback_period < 12:
    st.success("✅ ممتاز: المشروع يسترد رأس ماله في أقل من سنة. مخاطرة منخفضة.")
else:
    st.warning("ℹ️ تنبيه: فترة الاسترداد تزيد عن سنة. تأكد من ثبات المصاريف.")
