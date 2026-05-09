import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 1. إعدادات الصفحة والجماليات
st.set_page_config(page_title="Laundro-Sim Pro v8.5", layout="wide")

# 2. المحرك الحسابي المعتمد (The Core Engine)
def calculate_financials(data):
    # حساب الاستثمار الكلي
    total_inv = (data['n_w1'] * data['p_w1']) + \
                (data['n_w2'] * data['p_w2']) + \
                (data['n_dr'] * data['p_dr']) + \
                data['other_inv']
    
    # منطق التجفيف بالوحدات
    # صافي ربح التجفيف للزبون الواحد = عدد الوحدات * (سعر الوحدة - تكلفة طاقتها)
    dry_profit_per_cust = data['d_units_per_user'] * (data['d_unit_p'] - data['d_unit_c'])
    
    # هامش ربح الغسيل (سعر الخدمة + ربح التجفيف الملحق - تكاليف التشغيل والصيانة)
    maint_fixed = 20 # صيانة دورية لكل غسلة
    margin_w1 = (data['w1_p'] + dry_profit_per_cust) - (data['w1_c'] + maint_fixed)
    margin_w2 = (data['w2_p'] + dry_profit_per_cust) - (data['w2_c'] + maint_fixed)
    
    # الإيرادات الشهرية الإجمالية
    monthly_gross = ((margin_w1 * data['w1_d']) + (margin_w2 * data['w2_d'])) * data['d_pm']
    
    # المصاريف الثابتة والإهلاك
    monthly_dep = (total_inv - data['other_inv']) / (max(data['dep_years'], 1) * 12)
    total_fixed_costs = data['sal'] + data['f_ex'] + monthly_dep
    
    # الربح الصافي النهائي
    net_profit = monthly_gross - total_fixed_costs
    
    # نقطة التعادل (عدد الزبائن الكلي المطلوب شهرياً)
    avg_margin = (margin_w1 + margin_w2) / 2
    be_customers = total_fixed_costs / avg_margin if avg_margin > 0 else 0
    
    return {
        "total_inv": total_inv,
        "net_profit": int(net_profit),
        "monthly_dep": int(monthly_dep),
        "be_customers": int(be_customers),
        "total_fixed": int(total_fixed_costs),
        "dry_contribution": int(dry_profit_per_cust * (data['w1_d'] + data['w2_d']) * data['d_pm'])
    }

# 3. إدارة قاعدة البيانات (Persistence)
DB_FILE = "laundry_final_v8.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
    conn.close()

def save_val(key, val):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (key, val))
    conn.commit()
    conn.close()

def load_vals():
    conn = sqlite3.connect(DB_FILE)
    data = dict(conn.execute("SELECT * FROM settings").fetchall())
    conn.close()
    return data

init_db()
db_vals = load_vals()

# --- الواجهة الرئيسية ---
st.title("🚀 محاكي المغسلة الذكية v8.5")

with st.sidebar:
    st.header("🛡️ التحكم بالنظام")
    st.info("النسخة الكاملة: إدارة الوحدات + الحفظ التلقائي")
    if st.button("🗑️ إعادة ضبط المصنع"):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("DELETE FROM settings")
        conn.commit()
        st.rerun()

# توزيع المدخلات
tab1, tab2 = st.tabs(["📝 إدارة البيانات", "📊 التحليل المالي"])

with tab1:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏗️ الأصول (CapEx)")
        p_w1 = st.number_input("سعر غسالة 12kg", value=int(db_vals.get('p_w1', 180000)))
        p_w2 = st.number_input("سعر غسالة 18kg", value=int(db_vals.get('p_w2', 320000)))
        p_dr = st.number_input("سعر المجفف", value=int(db_vals.get('p_dr', 150000)))
        other_inv = st.number_input("ديكور وتأسيس", value=int(db_vals.get('other_inv', 200000)))
        save_val('p_w1', p_w1); save_val('p_w2', p_w2); save_val('p_dr', p_dr); save_val('other_inv', other_inv)

    with col2:
        st.subheader("🎫 التشغيل (OpEx)")
        w1_p = st.number_input("سعر الغسلة 12kg", value=int(db_vals.get('w1_p', 50)))
        w2_p = st.number_input("سعر الغسلة 18kg", value=int(db_vals.get('w2_p', 70)))
        w1_c = st.number_input("تكلفة منظفات (صغيرة)", value=110)
        w2_c = st.number_input("تكلفة منظفات (كبيرة)", value=180)
        save_val('w1_p', w1_p); save_val('w2_p', w2_p)

    with col3:
        st.subheader("🔥 نظام التجفيف")
        d_unit_p = st.number_input("سعر وحدة التجفيف", value=100)
        d_unit_c = st.number_input("تكلفة طاقة الوحدة", value=15)
        d_units = st.slider("وحدات/زبون", 1.0, 4.0, 2.0)
        salaries = st.number_input("رواتب وإيجار", value=45000)

    # بيانات التدفق اليومي
    st.divider()
    w1_d = st.slider("عدد زبائن 12kg يومياً", 0, 50, 12)
    w2_d = st.slider("عدد زبائن 18kg يومياً", 0, 50, 8)

# تنفيذ الحسابات
data_pack = {
    'n_w1': 3, 'p_w1': p_w1, 'w1_p': w1_p, 'w1_c': w1_c, 'w1_d': w1_d,
    'n_w2': 2, 'p_w2': p_w2, 'w2_p': w2_p, 'w2_c': w2_c, 'w2_d': w2_d,
    'n_dr': 3, 'p_dr': p_dr, 'd_unit_p': d_unit_p, 'd_unit_c': d_unit_c, 
    'd_units_per_user': d_units, 'd_pm': 30, 'sal': salaries, 'f_ex': 0, 
    'other_inv': other_inv, 'dep_years': 5
}

res = calculate_financials(data_pack)

with tab2:
    # النتائج الكبيرة
    k1, k2, k3 = st.columns(3)
    k1.metric("إجمالي الاستثمار", f"{res['total_inv']:,} دج")
    
    if res['net_profit'] > 0:
        k2.metric("الربح الصافي (شهرياً)", f"{res['net_profit']:,} دج", delta="مربح")
    else:
        k2.metric("الربح الصافي (شهرياً)", f"{res['net_profit']:,} دج", delta="خسارة", delta_color="inverse")
    
    k3.metric("نقطة التعادل", f"{res['be_customers']} زبون/شهر")

    st.divider()
    
    # الرسوم البيانية
    c_chart, c_info = st.columns([2, 1])
    
    with c_chart:
        fig, ax = plt.subplots(figsize=(8, 4))
        categories = ['Fixed Costs', 'Drying Profit', 'Net Profit']
        vals = [res['total_fixed'], res['dry_contribution'], max(0, res['net_profit'])]
        ax.bar(categories, vals, color=['#e74c3c', '#f1c40f', '#2ecc71'])
        ax.set_title("تحليل التدفقات المالية (دج)")
        st.pyplot(fig)

    with c_info:
        st.help("نقطة التعادل تعني أنك تحتاج لخدمة عدد الزبائن الموضح أعلاه شهرياً لتغطي كافة مصاريفك (بما في ذلك استرداد قيمة الأجهزة).")
        st.write(f"💡 **نصيحة PO:** التجفيف يساهم بـ **{res['dry_contribution']:,} دج** في دخلك. بدون التجفيف، سيكون مشروعك في خطر!")
