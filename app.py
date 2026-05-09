import streamlit as st
import matplotlib.pyplot as plt

# 1. إعدادات الصفحة والتنسيق الاحترافي
st.set_page_config(page_title="Laundro-Sim Pro v9.9", layout="wide")

# 2. دالة التنسيق المالي (The Monetary Formatter)
# هذه الدالة تحول الرقم العادي إلى شكل مالي سهل القراءة جداً
def dzd_format(value):
    return f"{value:,.0f} دج"

# 3. المحرك المالي المعتمد
def calculate_financials(data):
    total_inv = (data['qty_w12'] * data['p_w12']) + (data['qty_w18'] * data['p_w18']) + \
                (data['qty_dr'] * data['p_dr']) + data['setup']
    
    dry_profit_per_user = data['dry_units'] * (data['dry_p'] - data['dry_c'])
    margin_w12 = (data['srv_w12'] + dry_profit_per_user) - (110 + 20)
    margin_w18 = (data['srv_w18'] + dry_profit_per_user) - (180 + 20)
    
    monthly_gross = ((margin_w12 * data['cust_12']) + (margin_w18 * data['cust_18'])) * 30
    monthly_dep = (total_inv - data['setup']) / (5 * 12)
    total_fixed = data['fixed'] + monthly_dep
    
    net_profit = monthly_gross - total_fixed
    
    return {
        "total_inv": total_inv, "net_profit": int(net_profit),
        "break_even": int(total_fixed / ((margin_w12 + margin_w18) / 2)) if (margin_w12 + margin_w18) > 0 else 0,
        "total_fixed": int(total_fixed), "depreciation": int(monthly_dep),
        "dry_share": int(dry_profit_per_user * (data['cust_12'] + data['cust_18']) * 30)
    }

# --- واجهة المستخدم الرئيسية ---
st.title("🚀 محاكي المغسلة الذكية - v9.9")
st.markdown("##### *تنسيق مالي شامل لجميع الأسعار بدون استثناء*")
st.divider()

col_in, col_out = st.columns([2.2, 1])

with col_in:
    st.subheader("📝 إدخال البيانات (المنسق المالي مفعل)")
    
    # القسم الأول: الاستثمارات
    with st.expander("🏗️ 1. تكاليف الأصول والتجهيز", expanded=True):
        c1, c2, c3 = st.columns(3)
        p_w12 = c1.number_input("سعر غسالة 12 كغ", value=180000, step=5000, format="%d")
        st.write(f"🔍 {dzd_format(p_w12)}") # Formatter مالي أسفل الحقل
        
        p_w18 = c2.number_input("سعر غسالة 18 كغ", value=320000, step=5000, format="%d")
        st.write(f"🔍 {dzd_format(p_w18)}")
        
        p_dr = c3.number_input("سعر المجفف", value=150000, step=5000, format="%d")
        st.write(f"🔍 {dzd_format(p_dr)}")
        
        setup_c = st.number_input("تكاليف التهيئة والديكور", value=200000, step=10000, format="%d")
        st.write(f"🔍 المجموع: {dzd_format(setup_c)}")

    # القسم الثاني: التشغيل
    st.subheader("💰 2. تسعير الخدمات")
    o1, o2 = st.columns(2)
    with o1:
        st.info("الغسالة الصغيرة (12 كغ)")
        srv_12 = st.number_input("سعر الخدمة (دج)", value=50, step=10, format="%d")
        st.write(f"📝 {dzd_format(srv_12)}")
        c_12 = st.number_input("عدد الزبائن يومياً", value=12, step=1)
    
    with o2:
        st.info("الغسالة الكبيرة (18 كغ)")
        srv_18 = st.number_input("سعر الخدمة (دج) ", value=70, step=10, format="%d")
        st.write(f"📝 {dzd_format(srv_18)}")
        c_18 = st.number_input("عدد الزبائن يومياً ", value=8, step=1)

    # القسم الثالث: التجفيف والمصاريف
    st.subheader("🔥 3. نظام التجفيف والمصاريف")
    d1, d2, d3 = st.columns(3)
    d_p = d1.number_input("سعر وحدة التجفيف", value=100, step=10, format="%d")
    st.write(f"🔥 {dzd_format(d_p)}")
    
    d_u = d2.number_input("عدد الوحدات/زبون", value=2.0, step=0.5)
    
    f_c = d3.number_input("كراء + رواتب", value=45000, step=1000, format="%d")
    st.write(f"🏢 {dzd_format(f_c)}")

# الحسابات
data = {
    'qty_w12': 3, 'p_w12': p_w12, 'srv_w12': srv_12, 'cust_12': c_12,
    'qty_w18': 2, 'p_w18': p_w18, 'srv_w18': srv_18, 'cust_18': c_18,
    'qty_dr': 3, 'p_dr': p_dr, 'dry_p': d_p, 'dry_c': 15, 'dry_units': d_u,
    'fixed': f_c, 'setup': setup_c
}
res = calculate_financials(data)

with col_out:
    st.subheader("📊 لوحة التحليل المالي")
    
    # عرض الربح مع التنسيق المالي
    p_color = "green" if res['net_profit'] > 0 else "red"
    st.markdown(f"""
    <div style="padding:15px; border-radius:10px; background-color:#f8f9fa; border-right: 8px solid {p_color}; text-align:right;">
        <p style="margin:0; font-size:16px;">صافي الربح الشهري</p>
        <h2 style="margin:0; color:{p_color};">{dzd_format(res['net_profit'])}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("رأس المال المطلوب", dzd_format(res['total_inv']))
    st.metric("الإهلاك الشهري", dzd_format(res['depreciation']))
    st.metric("نقطة التعادل", f"{res['break_even']} زبون/شهر")
    
    st.divider()
    
    # الرسم البياني (English Labels)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(['Operating Costs', 'Drying Profit'], [res['total_fixed'], res['dry_share']], color=['#FF4B4B', '#2ECC71'])
    ax.set_title("Financial Performance (Monthly)")
    ax.set_ylabel("Amount (DZD)")
    st.pyplot(fig)

st.markdown("---")
st.caption("تم تطبيق المنسق المالي (DZD Formatter) على جميع الحقول لضمان دقة القراءة.")
