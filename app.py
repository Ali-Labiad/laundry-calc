import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Laundro-Sim Pro v6.1",
    layout="wide",
    initial_sidebar_state="expanded"
)

# دالة معالجة النصوص العربية للرسوم البيانية
def fix_ar(text):
    try:
        return get_display(reshape(text))
    except:
        return text

# 2. نظام تهيئة الذاكرة (Session State) لضمان عدم اختفاء البيانات
if 'n_w1' not in st.session_state:
    defaults = {
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
    for k, v in defaults.items():
        st.session_state[k] = v

# --- العنوان والوصف ---
st.title("🚀 محاكي المغسلة الذكية الاحترافي - v6.1")
st.caption("نسخة مطورة: تشمل تحليل الأصول، الإهلاك، وحماية البيانات من الفقدان")

# --- زر إعادة الضبط ---
if st.sidebar.button("🔄 إعادة ضبط كافة القيم"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- القسم الأول: قائمة الأصول والاستثمار الأولي ---
st.header("🏗️ 1. هيكل الاستثمار (Assets)")
with st.container():
    col_inv1, col_inv2, col_inv3 = st.columns(3)
    
    with col_inv1:
        st.subheader("🧺 الغسالات المتوسطة (12kg)")
        n_w1 = st.number_input("عدد الأجهزة", min_value=0, key="n_w1")
        p_w1 = st.number_input("سعر الجهاز الواحد (دج)", min_value=0, step=5000, key="p_w1")
        total_w1 = n_w1 * p_w1
        st.info(f"إجمالي: {total_w1:,.0f} دج")

    with col_inv2:
        st.subheader("🐘 الغسالات العملاقة (18kg)")
        n_w2 = st.number_input("عدد الأجهزة ", min_value=0, key="n_w2")
        p_w2 = st.number_input("سعر الجهاز الواحد  (دج)", min_value=0, step=5000, key="p_w2")
        total_w2 = n_w2 * p_w2
        st.info(f"إجمالي: {total_w2:,.0f} دج")

    with col_inv3:
        st.subheader("🔥 مجففات الغاز الذكية")
        n_dr = st.number_input("عدد المجففات", min_value=0, key="n_dr")
        p_dr = st.number_input("سعر المجفف الواحد (دج)", min_value=0, step=5000, key="p_dr")
        total_dr = n_dr * p_dr
        st.info(f"إجمالي: {total_dr:,.0f} دج")

    st.markdown("---")
    c_inv_a, c_inv_b = st.columns(2)
    other_inv = c_inv_a.number_input("مصاريف التأسيس (ديكور، رخص، سباكة)", min_value=0, key="other_inv")
    dep_years = c_inv_b.slider("العمر الافتراضي للأجهزة (سنوات لتجديد الأسطول)", 1, 15, key="dep_years")
    
    total_investment = total_w1 + total_w2 + total_dr + other_inv
    # حساب الإهلاك الشهري (القسط الشهري لتجديد الماكينات)
    monthly_depreciation = (total_w1 + total_w2 + total_dr) / (max(dep_years, 1) * 12)

# --- القسم الثاني: التشغيل والأسعار ---
st.header("💰 2. استراتيجية التشغيل والتسعير")
col_opt1, col_opt2 = st.columns(2)

with col_opt1:
    st.markdown("#### 💵 تسعير الخدمات والإقبال")
    w1_price = st.number_input("سعر غسلة (12kg)", key="w1_p")
    w1_daily = st.number_input("متوسط الزبائن يومياً (12kg)", key="w1_d")
    w1_cost = st.number_input("تكلفة المنظفات/غسلة (12kg)", key="w1_c")
    st.write("---")
    w2_price = st.number_input("سعر غسلة (18kg)", key="w2_p")
    w2_daily = st.number_input("متوسط الزبائن يومياً (18kg)", key="w2_d")
    w2_cost = st.number_input("تكلفة المنظفات/غسلة (18kg)", key="w2_c")

with col_opt2:
    st.markdown("#### 📊 المصاريف الثابتة والتجفيف")
    dryer_unit_price = st.number_input("سعر وحدة التجفيف (مثلاً 15 دقيقة)", key="d_up")
    dryer_units_avg = st.number_input("متوسط عدد الوحدات لكل زبون", key="d_ua")
    dryer_energy_cost = st.number_input("تكلفة الطاقة/الغاز لكل وحدة", key="d_ec")
    st.write("---")
    salary = st.number_input("رواتب العمال شهرياً", key="sal")
    fixed_extra = st.number_input("إيجار + فواتير + أخرى", key="f_ex")
    days_per_month = st.number_input("أيام العمل في الشهر", key="d_pm")

# --- 3. محرك الحسابات (Logic Engine) ---
maint_per_cycle = 20 # مبلغ تقديري للصيانة الدورية لكل دورة
dry_net_per_cust = (dryer_units_avg * dryer_unit_price) - (dryer_units_avg * dryer_energy_cost)

# صافي ربح الزبون الواحد من كل نوع
p_w1_single = (w1_price + dry_net_per_cust) - (w1_cost + maint_per_cycle)
p_w2_single = (w2_price + dry_net_per_cust) - (w2_cost + maint_per_cycle)

# الدخل الشهري الإجمالي
monthly_revenue = ((w1_price * w1_daily) + (w2_price * w2_daily) + (dryer_unit_price * dryer_units_avg * (w1_daily + w2_daily))) * days_per_month
monthly_gross_profit = ((p_w1_single * w1_daily) + (p_w2_single * w2_daily)) * days_per_month
ebitda = monthly_gross_profit - (salary + fixed_extra) # الربح قبل الإهلاك
net_profit_real = ebitda - monthly_depreciation # الربح الصافي النهائي

# التحليلات الاستراتيجية
roi_annual = (net_profit_real * 12 / total_investment) * 100 if total_investment > 0 else 0
payback_months = total_investment / net_profit_real if net_profit_real > 0 else float('inf')

# الطاقة الاستيعابية
max_cycles_per_day = 12
util_w1 = (w1_daily / (max(n_w1, 1) * max_cycles_per_day)) * 100 if n_w1 > 0 else 0
util_w2 = (w2_daily / (max(n_w2, 1) * max_cycles_per_day)) * 100 if n_w2 > 0 else 0

# --- 4. لوحة النتائج (Dashboard) ---
st.divider()
st.header("📈 3. النتائج والتحليل المالي")

k1, k2, k3, k4 = st.columns(4)

# الحالة المالية للربح
if net_profit_real > 0:
    k1.metric("صافي الربح الحقيقي (شهري)", f"{net_profit_real:,.0f} دج")
    k2.metric("فترة استرداد رأس المال", f"{payback_months:.1f} شهر")
else:
    k1.metric("صافي الربح الحقيقي (شهري)", f"{net_profit_real:,.0f} دج", delta="- خسارة", delta_color="inverse")
    k2.metric("فترة استرداد رأس المال", "∞ (غير محدد)")

k3.metric("مخصص تجديد الأجهزة", f"{monthly_depreciation:,.0f} دج", help="مبلغ يجب ادخاره شهرياً لشراء أجهزة جديدة مستقبلاً")
k4.metric("العائد السنوي (ROI)", f"{roi_annual:.1f} %")

# --- الرسوم البيانية والتحليل التشغيلي ---
tab1, tab2 = st.tabs(["📊 مسار النمو", "⚙️ تحليل الطاقة التشغيلية"])

with tab1:
    months = np.arange(0, 37) # 3 سنوات
    cash_flow = (net_profit_real * months) - total_investment
    fig, ax = plt.subplots(figsize=(10, 4))
    color = '#2ecc71' if net_profit_real > 0 else '#e74c3c'
    ax.plot(months, cash_flow, color=color, linewidth=3)
    ax.axhline(0, color='black', linestyle='--', alpha=0.3)
    ax.set_title(fix_ar("توقعات التدفق النقدي التراكمي (3 سنوات)"))
    ax.set_xlabel(fix_ar("الشهر"))
    ax.set_ylabel(fix_ar("صافي القيمة (دج)"))
    st.pyplot(fig)

with tab2:
    st.subheader("💡 كفاءة استخدام الأسطول")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write(f"**إشغال غسالات 12kg:** {util_w1:.1f}%")
        st.progress(min(util_w1/100, 1.0))
        if util_w1 > 85: st.warning("⚠️ الغسالات المتوسطة تعمل بأقصى طاقتها تقريباً!")

    with c2:
        st.write(f"**إشغال غسالات 18kg:** {util_w2:.1f}%")
        st.progress(min(util_w2/100, 1.0))
        if util_w2 > 85: st.warning("⚠️ الغسالات العملاقة تحت ضغط عالٍ!")

    st.info(f"""
    **ملاحظات تشغيلية:**
    * إجمالي الاستثمار في المعدات: {total_w1+total_w2+total_dr:,.0f} دج.
    * إجمالي الدخل الشهري (السيولة الداخلة): {monthly_revenue:,.0f} دج.
    * نقطة التعادل اليومية: {(salary + fixed_extra + monthly_depreciation) / (days_per_month * ((p_w1_single + p_w2_single)/2)) if (p_w1_single+p_w2_single) > 0 else 0:.1f} زبون/يوم.
    """)
