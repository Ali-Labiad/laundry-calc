import streamlit as st
import matplotlib.pyplot as plt

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Laundro-Sim Pro v10.2", layout="wide")

# 2. المنسق المالي (لإضافة العملة والتنسيق)
def fmt_dzd(value):
    return f"{value:,.2f} دج"

# 3. المحرك المالي (Financial Engine)
def calculate_financials(data):
    # حساب الاستثمار الكلي بناءً على الكمية × السعر
    inv_w12 = data['qty_w12'] * data['p_w12']
    inv_w18 = data['qty_w18'] * data['p_w18']
    inv_dr = data['qty_dr'] * data['p_dr']
    total_inv = inv_w12 + inv_w18 + inv_dr + data['setup']
    
    # حساب ربح التجفيف الصافي لكل زبون (السعر - التكلفة المتغيرة كالغاز)
    dry_profit_per_user = data['dry_units'] * (data['dry_p'] - data['dry_c'])
    
    # حساب هوامش الربح لكل غسلة (شاملة ربح التجفيف المتوقع)
    # ملاحظة: تم إضافة 20 دج كتكاليف متغيرة إضافية (ماء/كهرباء) لكل دورة
    margin_w12 = (data['srv_w12'] + dry_profit_per_user) - (data['det_12'] + 20)
    margin_w18 = (data['srv_w18'] + dry_profit_per_user) - (data['det_18'] + 20)
    
    # الحسابات الشهرية
    monthly_gross = ((margin_w12 * data['cust_12']) + (margin_w18 * data['cust_18'])) * 30
    monthly_dep = (total_inv - data['setup']) / (5 * 12)  # إهلاك على 5 سنوات
    total_fixed = data['fixed'] + monthly_dep
    
    net_profit = int(monthly_gross - total_fixed)
    
    return {
        "total_inv": total_inv, 
        "net_profit": net_profit,
        "be_point": int(total_fixed / ((margin_w12 + margin_w18) / 2)) if (margin_w12 + margin_w18) > 0 else 0,
        "depreciation": int(monthly_dep), 
        "total_fixed": int(total_fixed),
        "dry_share": int(dry_profit_per_user * (data['cust_12'] + data['cust_18']) * 30)
    }

# --- واجهة المستخدم (UI) ---
st.title("📊 محاكي المغسلة الذكية - v10.2")
st.markdown("##### *نظام متكامل لإدارة الأصول وتحليل الربحية - مشروع جيجل*")
st.divider()

# تقسيم الشاشة إلى مدخلات (يسار) ونتائج (يمين)
col_in, col_out = st.columns([2.2, 1])

with col_in:
    st.subheader("⚙️ إعدادات النموذج الاستثماري")
    
    # القسم 1: الأصول (الأعداد والأسعار)
    with st.expander("🏗️ 1. تجهيز الأصول والكميات", expanded=True):
        # تنسيق الأعمدة لعرض العدد بجانب السعر
        r1_c1, r1_c2 = st.columns([1, 2])
        qty_12 = r1_c1.number_input("عدد غسالات 12 كغ", value=3, step=1)
        p_w12 = r1_c2.number_input("سعر الوحدة 12 كغ (دج)", value=180000, step=5000)
        
        r2_c1, r2_c2 = st.columns([1, 2])
        qty_18 = r2_c1.number_input("عدد غسالات 18 كغ", value=2, step=1)
        p_w18 = r2_c2.number_input("سعر الوحدة 18 كغ (دج)", value=320000, step=5000)
        
        r3_c1, r3_c2 = st.columns([1, 2])
        qty_dr = r3_c1.number_input("عدد المجففات", value=3, step=1)
        p_dr = r3_c2.number_input("سعر وحدة المجفف (دج)", value=150000, step=5000)
        
        st.divider()
        setup_c = st.number_input("تكاليف التهيئة، السباكة والديكور (دج)", value=200000, step=10000)

    # القسم 2: الأسعار والتشغيل (بناءً على تحديثات الأسعار الأخيرة)
    st.subheader("💰 2. التشغيل اليومي والأسعار")
    o1, o2 = st.columns(2)
    with o1:
        st.info("الفئة الصغيرة (12 كغ)")
        srv_12 = st.number_input("سعر الخدمة (الحزمة)", value=50, step=10, key="s12") # تحديث السعر لـ 50 دج
        det_12 = st.number_input("تكلفة المنظفات/دورة", value=110, step=5, key="d12")
        c_12 = st.number_input("الزبائن يومياً (صغيرة)", value=12, step=1)
    
    with o2:
        st.info("الفئة الكبيرة (18 كغ)")
        srv_18 = st.number_input("سعر الخدمة (الحزمة) ", value=70, step=10, key="s18") # تحديث السعر لـ 70 دج
        det_18 = st.number_input("تكلفة المنظفات/دورة ", value=180, step=5, key="d18")
        c_18 = st.number_input("الزبائن يومياً (كبيرة)", value=8, step=1)

    # القسم 3: المصاريف الثابتة والتجفيف
    st.subheader("🔥 3. التكاليف الشهرية والتجفيف")
    d1, d2, d3 = st.columns(3)
    d_p = d1.number_input("سعر دورة التجفيف", value=100, step=10)
    d_u = d2.number_input("دورة تجفيف/زبون", value=2.0, step=0.5)
    f_c = d3.number_input("كراء + رواتب + كهرباء", value=45000, step=1000)

# تجميع البيانات وإرسالها للمحرك
data = {
    'qty_w12': qty_12, 'p_w12': p_w12, 'srv_w12': srv_12, 'det_12': det_12, 'cust_12': c_12,
    'qty_w18': qty_18, 'p_w18': p_w18, 'srv_w18': srv_18, 'det_18': det_18, 'cust_18': c_18,
    'qty_dr': qty_dr, 'p_dr': p_dr, 'dry_p': d_p, 'dry_c': 15, 'dry_units': d_u,
    'fixed': f_c, 'setup': setup_c
}
res = calculate_financials(data)

# --- عرض النتائج (العمود الجانبي) ---
with col_out:
    st.subheader("📈 نتائج التحليل")
    
    p_color = "green" if res['net_profit'] > 0 else "red"
    
    # عرض الاستثمار الكلي بشكل بارز
    st.metric("رأس المال المطلوب", fmt_dzd(res['total_inv']))
    
    # عرض صافي الربح بتصميم مخصص
    st.markdown(f"""
    <div style="padding:20px; border-radius:10px; background-color:#f8f9fa; border-right: 10px solid {p_color}; margin-bottom:20px;">
        <p style="margin:0; font-size:14px; color:#666;">صافي الربح الشهري المتوقع</p>
        <h2 style="margin:0; color:{p_color};">{fmt_dzd(res['net_profit'])}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("نقطة التعادل", f"{res['be_point']} زبون/شهر")
    st.metric("الإهلاك الشهري (توفير للأجهزة)", fmt_dzd(res['depreciation']))
    
    st.divider()
    
    # رسم بياني لتوزيع النتائج
    if res['net_profit'] > 0:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie([res['total_fixed'], res['net_profit']], 
               labels=['Costs', 'Profit'], 
               autopct='%1.1f%%', colors=['#FF4B4B', '#2ECC71'],
               startangle=90)
        ax.set_title("Monthly Revenue Breakdown")
        st.pyplot(fig)
    else:
        st.warning("الربح حالياً سالب، يرجى مراجعة التكاليف أو زيادة عدد الزبائن.")

st.markdown("---")
st.caption("Laundro-Sim Pro v10.2 | تم تحديث الأسعار والأعداد وفقاً لآخر التعليمات.")
