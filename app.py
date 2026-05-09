import streamlit as st
import matplotlib.pyplot as plt

# 1. إعدادات الصفحة والهوية البصرية
st.set_page_config(page_title="Laundro-Sim Pro v9.7", layout="wide")

# 2. المحرك المالي الاحترافي
def calculate_financials(data):
    # إجمالي الاستثمار الرأسمالي (CapEx)
    total_inv = (data['w12_qty'] * data['p_w12']) + \
                (data['w18_qty'] * data['p_w18']) + \
                (data['dryer_qty'] * data['p_dryer']) + \
                data['setup_costs']
    
    # ربح التجفيف = عدد الوحدات * (سعر الوحدة - تكلفة الطاقة)
    dry_profit_per_user = data['dry_units'] * (data['dry_price'] - data['dry_cost'])
    
    # هوامش الربح لكل دورة غسيل (تشمل ربح التجفيف الملحق)
    maint_buffer = 20  # احتياطي صيانة لكل غسلة
    margin_w12 = (data['srv_p_w12'] + dry_profit_per_user) - (data['det_w12'] + maint_buffer)
    margin_w18 = (data['srv_p_w18'] + dry_profit_per_user) - (data['det_w18'] + maint_buffer)
    
    # التدفق المالي الشهري الإجمالي
    monthly_gross = ((margin_w12 * data['w12_daily']) + (margin_w18 * data['w18_daily'])) * data['work_days']
    
    # حساب الإهلاك الشهري (تآكل قيمة الأجهزة)
    monthly_depreciation = (total_inv - data['setup_costs']) / (max(data['dep_years'], 1) * 12)
    
    # المصاريف الثابتة الكلية (كراء + رواتب + إهلاك)
    total_fixed_monthly = data['fixed_costs'] + monthly_depreciation
    
    # المقاييس النهائية
    net_profit = monthly_gross - total_fixed_monthly
    avg_margin = (margin_w12 + margin_w18) / 2
    break_even = total_fixed_monthly / avg_margin if avg_margin > 0 else 0
    
    return {
        "total_inv": total_inv,
        "net_profit": int(net_profit),
        "break_even": int(break_even),
        "total_fixed": int(total_fixed_monthly),
        "depreciation": int(monthly_depreciation),
        "dry_contribution": int(dry_profit_per_user * (data['w12_daily'] + data['w18_daily']) * data['work_days'])
    }

# --- واجهة المستخدم (UI) ---
st.title("📊 محاكي مشروع المغسلة الذكية")
st.markdown("##### *لوحة تخطيط الاستثمار والربحية - جيجل، الجزائر*")
st.divider()

# دالة لتنسيق المبالغ المالية بالدينار الجزائري
def fmt_dzd(val): return f"{val:,.0f} دج"

# تقسيم الواجهة إلى قسمين
col_inputs, col_results = st.columns([2.3, 1])

with col_inputs:
    st.subheader("⚙️ مدخلات البيانات")
    
    # 1. تكاليف الأصول والاستثمار الأولي
    with st.expander("🏗️ 1. Equipment & Fixed Assets (الأجهزة والتهيئة)", expanded=True):
        c1, c2, c3 = st.columns(3)
        p_w12 = c1.number_input("Unit Price: Wash 12kg", value=180000, step=5000)
        p_w18 = c2.number_input("Unit Price: Wash 18kg", value=320000, step=5000)
        p_dry = c3.number_input("Unit Price: Dryer", value=150000, step=5000)
        setup_c = st.number_input("Setup & Renovation (تهيئة المحل)", value=200000, step=10000)

    # 2. تسعير الخدمات والتدفق اليومي
    st.subheader("💰 2. Daily Operations (التشغيل اليومي)")
    o1, o2 = st.columns(2)
    with o1:
        st.info("Wash 12kg (Small)")
        srv_p_12 = st.number_input("Service Price (DZD)", value=50, step=10, key="srv12")
        daily_12 = st.number_input("Daily Customers", value=12, step=1, key="day12")
    
    with o2:
        st.info("Wash 18kg (Large)")
        srv_p_18 = st.number_input("Service Price (DZD) ", value=70, step=10, key="srv18")
        daily_18 = st.number_input("Daily Customers ", value=8, step=1, key="day18")

    # 3. إعدادات التجفيف والمصاريف الثابتة
    st.subheader("🔥 3. Drying & Fixed Costs (التجفيف والمصاريف)")
    d1, d2, d3 = st.columns(3)
    dry_up = d1.number_input("Dry Unit Price", value=100, step=10)
    dry_units = d2.number_input("Units per User", value=2.0, step=0.5)
    fixed_op = d3.number_input("Fixed Costs (رواتب وكراء)", value=45000, step=1000)

# تجميع البيانات وإجراء الحسابات
data_bundle = {
    'w12_qty': 3, 'p_w12': p_w12, 'srv_p_w12': srv_p_12, 'det_w12': 110, 'w12_daily': daily_12,
    'w18_qty': 2, 'p_w18': p_w18, 'srv_p_w18': srv_p_18, 'det_w18': 180, 'w18_daily': daily_18,
    'dryer_qty': 3, 'p_dryer': p_dry, 'dry_price': dry_up, 'dry_cost': 15, 'dry_units': dry_units,
    'work_days': 30, 'fixed_costs': fixed_op, 'setup_costs': setup_c, 'dep_years': 5
}

res = calculate_financials(data_bundle)

# --- عرض النتائج في العمود الجانبي ---
with col_results:
    st.subheader("📈 ملخص التحليل المالي")
    
    # بطاقة الربح الصافي
    res_color = "green" if res['net_profit'] > 0 else "red"
    st.markdown(f"""
    <div style="padding:20px; border-radius:10px; background-color:#f8f9fa; border-right: 10px solid {res_color}; text-align:right;">
        <p style="margin:0; font-size:14px; color:#555;">الربح الصافي الشهري</p>
        <h2 style="margin:0; color:{res_color};">{fmt_dzd(res['net_profit'])}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("إجمالي رأس المال المطلوب", fmt_dzd(res['total_inv']))
    st.metric("نقطة التعادل (زبون/شهر)", f"{res['break_even']} زبون")
    st.metric("الإهلاك الشهري للأجهزة", fmt_dzd(res['depreciation']))
    
    st.divider()
    
    # الرسم البياني التحليلي بالإنجليزية
    fig, ax = plt.subplots(figsize=(5, 4))
    labels = ['Fixed Costs', 'Drying Profit']
    values = [res['total_fixed'], res['dry_contribution']]
    ax.bar(labels, values, color=['#e74c3c', '#2ecc71'])
    ax.set_title("Opex vs. Drying Revenue (Monthly)")
    ax.set_ylabel("DZD Amount")
    st.pyplot(fig)

    if res['net_profit'] <= 0:
        st.error("تنبيه: المشروع يسجل خسارة تشغيلية. يرجى رفع سعر الخدمة أو زيادة عدد الوحدات المستهلكة في التجفيف.")

st.markdown("---")
st.caption("Laundro-Sim Pro v9.7 | عملة النظام: الدينار الجزائري (DZD) | لغة التقارير: English Charts & Arabic UI")
