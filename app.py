import streamlit as st
import matplotlib.pyplot as plt

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Laundro-Sim Pro v10.5", layout="wide", page_icon="🧼")

# 2. المنسق المالي (الأداة السحرية لعرض العملة)
def fmt_dzd(value):
    return f"{value:,.2f} دج"

# 3. المحرك المالي الحسابي
def calculate_financials(data):
    # حساب الاستثمار الرأسمالي (CapEx)
    inv_total = (data['qty_w12'] * data['p_w12']) + \
                (data['qty_w18'] * data['p_w18']) + \
                (data['qty_dr'] * data['p_dr']) + data['setup']
    
    # حساب ربح التجفيف الصافي (المحرك الخفي للأرباح)
    dry_profit_per_user = data['dry_units'] * (data['dry_p'] - data['dry_c'])
    
    # حساب هوامش الربح لكل دورة غسيل
    margin_w12 = (data['srv_w12'] + dry_profit_per_user) - (data['det_12'] + 20)
    margin_w18 = (data['srv_w18'] + dry_profit_per_user) - (data['det_18'] + 20)
    
    # الحسابات الشهرية (30 يوم عمل)
    monthly_gross = ((margin_w12 * data['cust_12']) + (margin_w18 * data['cust_18'])) * 30
    monthly_dep = (inv_total - data['setup']) / (5 * 12)  # إهلاك الأجهزة على 5 سنوات
    total_fixed = data['fixed'] + monthly_dep
    
    net_profit = int(monthly_gross - total_fixed)
    
    return {
        "total_inv": inv_total, 
        "net_profit": net_profit,
        "be_point": int(total_fixed / ((margin_w12 + margin_w18) / 2)) if (margin_w12 + margin_w18) > 0 else 0,
        "depreciation": int(monthly_dep), 
        "total_fixed": int(total_fixed)
    }

# --- واجهة المستخدم (UI) ---
st.title("🧼 محاكي المغسلة الذكية - النسخة النهائية v10.5")
st.markdown("---")

col_in, col_out = st.columns([2.2, 1])

with col_in:
    st.subheader("⚙️ إعدادات النموذج")
    
    # القسم 1: الأصول والمعدات
    with st.expander("🏗️ 1. الأصول الرأسمالية (CapEx)", expanded=True):
        c1, c2 = st.columns([1, 2])
        qty_12 = c1.number_input("عدد غسالات 12 كغ", value=3, step=1)
        p_w12 = c2.number_input("سعر الوحدة 12 كغ (دج)", value=180000, step=5000, format="%d")
        c2.caption(f"💰 المبلغ المنسق: **{fmt_dzd(p_w12)}**") # ربط ديناميكي صحيح
        
        st.divider()
        
        c3, c4 = st.columns([1, 2])
        qty_18 = c3.number_input("عدد غسالات 18 كغ", value=2, step=1)
        p_w18 = c4.number_input("سعر الوحدة 18 كغ (دج)", value=320000, step=5000, format="%d")
        c4.caption(f"💰 المبلغ المنسق: **{fmt_dzd(p_w18)}**")
        
        st.divider()
        
        c5, c6 = st.columns([1, 2])
        qty_dr = c5.number_input("عدد المجففات", value=3, step=1)
        p_dr = c6.number_input("سعر المجفف الواحد (دج)", value=150000, step=5000, format="%d")
        c6.caption(f"💰 المبلغ المنسق: **{fmt_dzd(p_dr)}**")
        
        setup_c = st.number_input("تكاليف التهيئة والديكور (دج)", value=200000, step=10000, format="%d")
        st.caption(f"🔧 ميزانية التجهيز: **{fmt_dzd(setup_c)}**")

    # القسم 2: الأسعار والتشغيل
    with st.expander("💰 2. أسعار الخدمات والتشغيل اليومي"):
        o1, o2 = st.columns(2)
        with o1:
            st.info("الحزمة الصغيرة (12 كغ)")
            srv_12 = st.number_input("سعر الخدمة", value=50, key="s12")
            st.caption(f"عرض السعر: **{fmt_dzd(srv_12)}**")
            det_12 = st.number_input("تكلفة المنظفات/دورة", value=110.0, format="%.1f")
            c_12 = st.number_input("عدد الزبائن يومياً", value=12, key="c12")
        
        with o2:
            st.info("الحزمة الكبيرة (18 كغ)")
            srv_18 = st.number_input("سعر الخدمة ", value=70, key="s18")
            st.caption(f"عرض السعر: **{fmt_dzd(srv_18)}**")
            det_18 = st.number_input("تكلفة المنظفات/دورة ", value=180.0, format="%.1f")
            c_18 = st.number_input("عدد الزبائن يومياً ", value=8, key="c18")

# تجميع البيانات وحسابها
data = {
    'qty_w12': qty_12, 'p_w12': p_w12, 'srv_w12': srv_12, 'det_12': det_12, 'cust_12': c_12,
    'qty_w18': qty_18, 'p_w18': p_w18, 'srv_w18': srv_18, 'det_18': det_18, 'cust_18': c_18,
    'qty_dr': qty_dr, 'p_dr': p_dr, 'dry_p': 100, 'dry_c': 15, 'dry_units': 2.0,
    'fixed': 45000, 'setup': setup_c
}
res = calculate_financials(data)

# --- لوحة النتائج ---
with col_out:
    st.subheader("📈 التحليل المالي")
    
    st.metric("إجمالي رأس المال", fmt_dzd(res['total_inv']))
    
    p_color = "green" if res['net_profit'] > 0 else "red"
    st.markdown(f"""
    <div style="padding:20px; border-radius:10px; background-color:#f8f9fa; border-right: 10px solid {p_color};">
        <p style="margin:0; font-size:14px; color:#666;">صافي الربح الشهري</p>
        <h2 style="margin:0; color:{p_color};">{fmt_dzd(res['net_profit'])}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.metric("نقطة التعادل", f"{res['be_point']} زبون/شهر")
    st.metric("توفير للإهلاك (شهرياً)", fmt_dzd(res['depreciation']))

    if res['net_profit'] > 0:
        fig, ax = plt.subplots()
        ax.pie([res['total_fixed'], res['net_profit']], labels=['Costs', 'Profit'], 
               autopct='%1.1f%%', colors=['#FF4B4B', '#2ECC71'], startangle=90)
        st.pyplot(fig)
    else:
        st.error("تنبيه: التكاليف تتجاوز الأرباح!")

st.markdown("---")
st.caption("Laundro-Sim Pro v10.5 | تم الربط الديناميكي للمبالغ بنجاح.")
