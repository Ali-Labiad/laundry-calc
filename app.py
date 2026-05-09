import streamlit as st
import matplotlib.pyplot as plt

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro v10.0", layout="wide")

# 2. المنسق المالي الشامل (The Universal Monetary Formatter)
def fmt_dzd(value):
    return f"{value:,.0f} دج"

# 3. المحرك المالي المعالج (Fixed Financial Engine)
def calculate_financials(data):
    # حساب الاستثمار الكلي
    total_inv = (data['qty_w12'] * data['p_w12']) + (data['qty_w18'] * data['p_w18']) + \
                (data['qty_dr'] * data['p_dr']) + data['setup']
    
    # ربح التجفيف الصافي لكل زبون
    dry_profit_per_user = data['dry_units'] * (data['dry_p'] - data['dry_c'])
    
    # تصحيح الخلل: حساب الهامش بناءً على مدخلات المنظفات المتغيرة
    maint_fixed = 20 # تكلفة صيانة تقديرية لكل غسلة
    margin_w12 = (data['srv_w12'] + dry_profit_per_user) - (data['det_w12'] + maint_fixed)
    margin_w18 = (data['srv_w18'] + dry_profit_per_user) - (data['det_w18'] + maint_fixed)
    
    # حساب الإيراد الشهري (30 يوم عمل)
    monthly_gross = ((margin_w12 * data['cust_12']) + (margin_w18 * data['cust_18'])) * 30
    
    # حساب الإهلاك (Depreciation) - 5 سنوات
    monthly_dep = (total_inv - data['setup']) / (5 * 12)
    total_fixed_costs = data['fixed_costs'] + monthly_dep
    
    net_profit = monthly_gross - total_fixed_costs
    
    # نقطة التعادل
    avg_margin = (margin_w12 + margin_w18) / 2
    be_point = total_fixed_costs / avg_margin if avg_margin > 0 else 0
    
    return {
        "total_inv": total_inv,
        "net_profit": int(net_profit),
        "be_point": int(be_point),
        "total_fixed": int(total_fixed_costs),
        "depreciation": int(monthly_dep),
        "dry_contribution": int(dry_profit_per_user * (data['cust_12'] + data['cust_18']) * 30)
    }

# --- الواجهة البرمجية ---
st.title("🚀 محاكي المغسلة v10.0 - النسخة المعالجة")
st.markdown("##### *نظام مالي احترافي بـ Monetary Formatter شامل*")
st.divider()

col_in, col_out = st.columns([2.2, 1])

with col_in:
    st.subheader("📝 مدخلات البيانات (جميع الأسعار تخضع للتنسيق)")
    
    # القسم 1: الاستثمار
    with st.expander("🏗️ 1. تكاليف الأصول والتجهيز", expanded=True):
        c1, c2, c3 = st.columns(3)
        p_w12 = c1.number_input("سعر غسالة 12 كغ", value=180000, step=5000, format="%d")
        st.caption(f"💰 {fmt_dzd(p_w12)}")
        
        p_w18 = c2.number_input("سعر غسالة 18 كغ", value=320000, step=5000, format="%d")
        st.caption(f"💰 {fmt_dzd(p_w18)}")
        
        p_dr = c3.number_input("سعر المجفف", value=150000, step=5000, format="%d")
        st.caption(f"💰 {fmt_dzd(p_dr)}")
        
        setup_c = st.number_input("تكاليف التهيئة (Decor/Plumbing)", value=200000, step=10000, format="%d")
        st.caption(f"🏗️ {fmt_dzd(setup_c)}")

    # القسم 2: الخدمات والتشغيل
    st.subheader("💰 2. التشغيل والمنظفات")
    o1, o2 = st.columns(2)
    with o1:
        st.info("الغسالة الصغيرة (12 كغ)")
        srv_12 = st.number_input("سعر الخدمة (دج)", value=50, step=10, format="%d")
        st.caption(fmt_dzd(srv_12))
        det_12 = st.number_input("تكلفة المنظفات/غسلة (12 كغ)", value=110, step=5, format="%d")
        st.caption(fmt_dzd(det_12))
        c_12 = st.number_input("عدد الزبائن يومياً", value=12, step=1, key="c12")
    
    with o2:
        st.info("الغسالة الكبيرة (18 كغ)")
        srv_18 = st.number_input("سعر الخدمة (دج) ", value=70, step=10, format="%d")
        st.caption(fmt_dzd(srv_18))
        det_18 = st.number_input("تكلفة المنظفات/غسلة (18 كغ)", value=180, step=5, format="%d")
        st.caption(fmt_dzd(det_18))
        c_18 = st.number_input("عدد الزبائن يومياً ", value=8, step=1, key="c18")

    # القسم 3: التجفيف والمصاريف الثابتة
    st.subheader("🔥 3. التجفيف والمصاريف")
    d1, d2, d3 = st.columns(3)
    d_p = d1.number_input("سعر وحدة التجفيف", value=100, step=10, format="%d")
    st.caption(fmt_dzd(d_p))
    d_u = d2.number_input("الوحدات لكل زبون", value=2.0, step=0.5)
    f_c = d3.number_input("المصاريف (كراء + رواتب)", value=45000, step=1000, format="%d")
    st.caption(fmt_dzd(f_c))

# تجميع ومعالجة البيانات
data = {
    'qty_w12': 3, 'p_w12': p_w12, 'srv_w12': srv_12, 'det_w12': det_12, 'cust_12': c_12,
    'qty_w18': 2, 'p_w18': p_w18, 'srv_w18': srv_18, 'det_w18': det_18, 'cust_18': c_18,
    'qty_dr': 3, 'p_dr': p_dr, 'dry_p': d_p, 'dry_c': 15, 'dry_units': d_u,
    'fixed_costs': f_c, 'setup': setup_c
}
res = calculate_financials(data)

# --- لوحة النتائج ---
with col_out:
    st.subheader("📊 التحليل النهائي")
    
    # صافي الربح بتنسيق مالي بارز
    p_color = "green" if res['net_profit'] > 0 else "red"
    st.markdown(f"""
    <div style="padding:15px; border-radius:10px; background-color:#f8f9fa; border-right: 10px solid {p_color}; text-align:right;">
        <p style="margin:0; font-size:14px; font-weight:bold;">صافي الربح الشهري الحقيقي</p>
        <h2 style="margin:0; color:{p_color};">{fmt_dzd(res['net_profit'])}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("رأس المال الكلي", fmt_dzd(res['total_inv']))
    st.metric("الإهلاك الشهري للأجهزة", fmt_dzd(res['depreciation']))
    st.metric("نقطة التعادل", f"{res['be_point']} زبون/شهر")
    
    st.divider()
    
    # الرسم البياني (English Labels)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(['Operational Costs', 'Drying Profit'], [res['total_fixed'], res['dry_contribution']], color=['#FF4B4B', '#2ECC71'])
    ax.set_title("Profitability Breakdown")
    st.pyplot(fig)

st.markdown("---")
st.caption("تم إصلاح خلل تكاليف المنظفات وتعميم التنسيق المالي (DZD Formatter) على جميع الحقول.")
