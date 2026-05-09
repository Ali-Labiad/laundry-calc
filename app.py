import streamlit as st
import sqlite3
import matplotlib.pyplot as plt

# 1. إعدادات الصفحة والجماليات
st.set_page_config(page_title="Laundro-Sim Pro v8.8", layout="wide")

# 2. المحرك الحسابي (The Financial Logic)
def calculate_financials(data):
    # إجمالي الاستثمار
    total_inv = (data['n_w1'] * data['p_w1']) + (data['n_w2'] * data['p_w2']) + \
                (data['n_dr'] * data['p_dr']) + data['other_inv']
    
    # ربح التجفيف = عدد الوحدات * (سعر الوحدة - تكلفة الطاقة)
    dry_profit_per_cust = data['d_units'] * (data['d_unit_p'] - data['d_unit_c'])
    
    # هامش الربح لكل نوع غسالة (شامل ربح التجفيف الملحق)
    maint_fixed = 20  # صيانة لكل دورة
    margin_w1 = (data['w1_p'] + dry_profit_per_cust) - (data['w1_c'] + maint_fixed)
    margin_w2 = (data['w2_p'] + dry_profit_per_cust) - (data['w2_c'] + maint_fixed)
    
    # الإيراد الإجمالي الشهري
    monthly_gross = ((margin_w1 * data['w1_d']) + (margin_w2 * data['w2_d'])) * data['d_pm']
    
    # الإهلاك والمصاريف الثابتة
    monthly_dep = (total_inv - data['other_inv']) / (max(data['dep_years'], 1) * 12)
    total_fixed_costs = data['sal'] + monthly_dep
    
    # النتائج النهائية
    net_profit = monthly_gross - total_fixed_costs
    avg_margin = (margin_w1 + margin_w2) / 2
    be_customers = total_fixed_costs / avg_margin if avg_margin > 0 else 0
    
    return {
        "total_inv": total_inv,
        "net_profit": int(net_profit),
        "be_customers": int(be_customers),
        "total_fixed": int(total_fixed_costs),
        "dry_contribution": int(dry_profit_per_cust * (data['w1_d'] + data['w2_d']) * data['d_pm']),
        "monthly_dep": int(monthly_dep)
    }

# --- واجهة المستخدم التفاعلية ---

# الشريط الجانبي: مخصص لإعدادات "المحرك" (التجفيف والزمن)
with st.sidebar:
    st.header("🔥 تحكم التجفيف (المدخلات)")
    d_unit_p = st.select_slider("سعر وحدة التجفيف (دج)", options=[50, 70, 100, 120, 150, 200], value=100)
    d_units = st.slider("عدد الوحدات لكل زبون", 1.0, 5.0, 2.0, step=0.5)
    d_unit_c = st.number_input("تكلفة الطاقة/وحدة (دج)", value=15)
    
    st.divider()
    st.header("⏳ الإهلاك والوقت")
    dep_years = st.radio("عمر الأجهزة (سنوات)", [3, 5, 7, 10], index=1, horizontal=True)
    working_days = st.slider("أيام العمل/شهر", 20, 31, 30)
    
    if st.button("🗑️ تصفير الحسابات", use_container_width=True):
        st.rerun()

# الواجهة الرئيسية: مقسمة لمدخلات تشغيلية ونتائج بصرية
st.title("🚀 محاكي المغسلة الذكية - v8.8 التفاعلية")

col_inputs, col_visuals = st.columns([2, 1])

with col_inputs:
    with st.expander("🏗️ 1. تكاليف الأجهزة (الاستثمار الصافي)", expanded=False):
        c1, c2 = st.columns(2)
        p_w1 = c1.select_slider("سعر غسالة 12kg (ألف دج)", options=list(range(100000, 300001, 10000)), value=180000)
        p_w2 = c2.select_slider("سعر غسالة 18kg (ألف دج)", options=list(range(200000, 500001, 10000)), value=320000)
        p_dr = st.slider("سعر المجفف الواحد", 100000, 300000, 150000, step=5000)
        other_inv = st.number_input("تكاليف التأسيس (ديكور/سباكة)", value=200000)

    st.subheader("💰 2. إدارة التشغيل اليومي")
    
    # تحكم الغسالة الصغيرة
    st.markdown("#### 🧺 دورة 12kg")
    w1_p = st.select_slider("سعر البيع (دج)", options=[50, 70, 100, 150, 200, 300], value=50, key="w1_p")
    w1_d = st.slider("عدد الزبائن يومياً", 0, 50, 12, key="w1_d")
    
    st.divider()
    
    # تحكم الغسالة الكبيرة
    st.markdown("#### 🐘 دورة 18kg")
    w2_p = st.select_slider("سعر البيع (دج) ", options=[70, 100, 150, 200, 300, 400, 500], value=70, key="w2_p")
    w2_d = st.slider("عدد الزبائن يومياً ", 0, 40, 8, key="w2_d")
    
    st.divider()
    salaries = st.slider("المصاريف الثابتة (رواتب + كراء)", 20000, 150000, 45000, step=1000)

# تجميع البيانات وإرسالها للمحرك
data_pack = {
    'n_w1': 3, 'p_w1': p_w1, 'w1_p': w1_p, 'w1_c': 110, 'w1_d': w1_d,
    'n_w2': 2, 'p_w2': p_w2, 'w2_p': w2_p, 'w2_c': 180, 'w2_d': w2_d,
    'n_dr': 3, 'p_dr': p_dr, 
    'd_unit_p': d_unit_p, 'd_unit_c': d_unit_c, 'd_units': d_units,
    'd_pm': working_days, 'sal': salaries, 'other_inv': other_inv, 'dep_years': dep_years
}

res = calculate_financials(data_pack)

with col_visuals:
    st.markdown("### 📊 لوحة النتائج")
    
    st.metric("إجمالي الاستثمار", f"{res['total_inv']:,} دج")
    
    # تحديد لون وحالة الربح
    if res['net_profit'] > 0:
        st.metric("الربح الصافي النهائي", f"{res['net_profit']:,} دج", delta="مربح")
    else:
        st.metric("الربح الصافي النهائي", f"{res['net_profit']:,} دج", delta="خسارة تشغيلية", delta_color="inverse")
    
    st.metric("نقطة التعادل", f"{res['be_customers']} زبون/شهر")
    st.metric("الإهلاك الشهري", f"{res['monthly_dep']:,} دج")

    # الرسم البياني التحليلي
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(['Fixed Costs', 'Dry Profit'], [res['total_fixed'], res['dry_contribution']], color=['#FF4B4B', '#F1C40F'])
    ax.set_title("المصاريف مقابل أرباح التجفيف")
    st.pyplot(fig)

    if res['net_profit'] <= 0:
        st.warning("⚠️ نصيحة PO: السعر الحالي للغسيل لا يغطي المصاريف. اعتمد على 'سعر التجفيف' أو ارفع أسعار الغسيل للوصول للربحية.")
