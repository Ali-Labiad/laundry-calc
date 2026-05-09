import streamlit as st
import matplotlib.pyplot as plt

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro v10.1", layout="wide")

# 2. المنسق المالي (Formatter)
def fmt_dzd(value):
    return f"{value:,.0f} دج"

# 3. المحرك المالي
def calculate_financials(data):
    total_inv = (data['qty_w12'] * data['p_w12']) + (data['qty_w18'] * data['p_w18']) + \
                (data['qty_dr'] * data['p_dr']) + data['setup']
    
    dry_profit_per_user = data['dry_units'] * (data['dry_p'] - data['dry_c'])
    
    # حساب الهوامش بناءً على تكاليف المنظفات المدخلة
    margin_w12 = (data['srv_w12'] + dry_profit_per_user) - (data['det_12'] + 20)
    margin_w18 = (data['srv_w18'] + dry_profit_per_user) - (data['det_18'] + 20)
    
    monthly_gross = ((margin_w12 * data['cust_12']) + (margin_w18 * data['cust_18'])) * 30
    monthly_dep = (total_inv - data['setup']) / (5 * 12)
    total_fixed = data['fixed'] + monthly_dep
    
    return {
        "total_inv": total_inv, "net_profit": int(monthly_gross - total_fixed),
        "be_point": int(total_fixed / ((margin_w12 + margin_w18) / 2)) if (margin_w12 + margin_w18) > 0 else 0,
        "depreciation": int(monthly_dep), "total_fixed": int(total_fixed),
        "dry_share": int(dry_profit_per_user * (data['cust_12'] + data['cust_18']) * 30)
    }

# --- واجهة المستخدم (UI) ---
st.title("📊 محاكي المغسلة الذكية - v10.1")
st.markdown("##### *واجهة مستخدم نظيفة ومنظمة بدون تكرار للبيانات*")
st.divider()

col_in, col_out = st.columns([2.2, 1])

with col_in:
    st.subheader("⚙️ إعدادات المشروع")
    
    # القسم 1: تكاليف الأصول
    with st.expander("🏗️ 1. تكاليف التجهيز والأصول", expanded=True):
        c1, c2, c3 = st.columns(3)
        # تم إخفاء التسميات الفرعية المكررة ودمجها في الخانة
        p_w12 = c1.number_input("سعر غسالة 12 كغ (دج)", value=180000, step=5000)
        p_w18 = c2.number_input("سعر غسالة 18 كغ (دج)", value=320000, step=5000)
        p_dr = c3.number_input("سعر المجفف (دج)", value=150000, step=5000)
        
        setup_c = st.number_input("تكاليف التهيئة والديكور (دج)", value=200000, step=10000)

    # القسم 2: التشغيل والمنظفات
    st.subheader("💰 2. التشغيل والمنظفات")
    o1, o2 = st.columns(2)
    with o1:
        st.info("الغسالة الصغيرة (12 كغ)")
        srv_12 = st.number_input("سعر الخدمة", value=50, step=10, key="s12")
        det_12 = st.number_input("تكلفة المنظفات للغسلة الواحد", value=110, step=5, key="d12")
        c_12 = st.number_input("عدد الزبائن يومياً", value=12, step=1, key="c12")
    
    with o2:
        st.info("الغسالة الكبيرة (18 كغ)")
        srv_18 = st.number_input("سعر الخدمة ", value=70, step=10, key="s18")
        det_18 = st.number_input("تكلفة المنظفات للغسلة الواحدة ", value=180, step=5, key="d18")
        c_18 = st.number_input("عدد الزبائن يومياً ", value=8, step=1, key="c18")

    # القسم 3: التجفيف والمصاريف الثابتة
    st.subheader("🔥 3. التجفيف والمصاريف")
    d1, d2, d3 = st.columns(3)
    d_p = d1.number_input("سعر وحدة التجفيف", value=100, step=10)
    d_u = d2.number_input("الوحدات لكل زبون", value=2.0, step=0.5)
    f_c = d3.number_input("كراء + رواتب (شهرياً)", value=45000, step=1000)

# معالجة الحسابات
data = {
    'qty_w12': 3, 'p_w12': p_w12, 'srv_w12': srv_12, 'det_12': det_12, 'cust_12': c_12,
    'qty_w18': 2, 'p_w18': p_w18, 'srv_w18': srv_18, 'det_18': det_18, 'cust_18': c_18,
    'qty_dr': 3, 'p_dr': p_dr, 'dry_p': d_p, 'dry_c': 15, 'dry_units': d_u,
    'fixed': f_c, 'setup': setup_c
}
res = calculate_financials(data)

# --- عرض النتائج الجانبية ---
with col_out:
    st.subheader("📈 ملخص التحليل")
    
    p_color = "green" if res['net_profit'] > 0 else "red"
    st.markdown(f"""
    <div style="padding:20px; border-radius:10px; background-color:#f8f9fa; border-right: 10px solid {p_color}; text-align:right;">
        <p style="margin:0; font-size:14px;">صافي الربح الشهري</p>
        <h2 style="margin:0; color:{p_color};">{fmt_dzd(res['net_profit'])}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("رأس المال المطلوب", fmt_dzd(res['total_inv']))
    st.metric("نقطة التعادل", f"{res['be_point']} زبون/شهر")
    st.metric("الإهلاك الشهري للأجهزة", fmt_dzd(res['depreciation']))
    
    st.divider()
    
    # الرسم البياني بالإنجليزية
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(['Costs', 'Drying Income'], [res['total_fixed'], res['dry_share']], color=['#FF4B4B', '#2ECC71'])
    ax.set_title("Performance Analysis")
    st.pyplot(fig)

st.markdown("---")
st.caption("تم تنظيف الواجهة وإزالة الأرقام المكررة غير الضرورية.")
