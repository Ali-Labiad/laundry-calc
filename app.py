import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. إعدادات الصفحة
st.set_page_config(page_title="Laundro-Sim Pro v8.0", layout="wide")

# 2. المحرك الحسابي (Business Logic Layer) - خاضع للاختبار
def calculate_financials(data):
    # إجمالي الاستثمار
    total_inv = (data['n_w1'] * data['p_w1']) + \
                (data['n_w2'] * data['p_w2']) + \
                (data['n_dr'] * data['p_dr']) + \
                data['other_inv']
    
    # تكاليف تشغيلية (متغيرة وثابتة)
    maint_per_wash = 20
    dryer_energy_cost = 15
    
    # ربح التجفيف الصافي
    dry_net = (data['d_ua'] * data['d_up']) - (data['d_ua'] * dryer_energy_cost)
    
    # هامش ربح الغسلة الواحدة
    margin_w1 = (data['w1_p'] + dry_net) - (data['w1_c'] + maint_per_wash)
    margin_w2 = (data['w2_p'] + dry_net) - (data['w2_c'] + maint_per_wash)
    
    # الإيراد الشهري الإجمالي (قبل المصاريف الثابتة)
    monthly_gross_margin = ((margin_w1 * data['w1_d']) + (margin_w2 * data['w2_d'])) * data['d_pm']
    
    # الإهلاك والمصاريف الثابتة
    monthly_dep = (total_inv - data['other_inv']) / (max(data['dep_years'], 1) * 12)
    total_fixed_costs = data['sal'] + data['f_ex'] + monthly_dep
    
    # الربح الصافي
    net_profit = monthly_gross_margin - total_fixed_costs
    
    # حساب نقطة التعادل (عدد الغسلات المطلوبة شهرياً لتغطية التكاليف الثابتة)
    avg_margin = (margin_w1 + margin_w2) / 2
    break_even_units = total_fixed_costs / avg_margin if avg_margin > 0 else 0
    
    return {
        "total_inv": total_inv,
        "net_profit": int(net_profit),
        "monthly_dep": int(monthly_dep),
        "break_even": int(break_even_units),
        "margin_w1": margin_w1,
        "margin_w2": margin_w2,
        "fixed_costs": total_fixed_costs
    }

# 3. نظام اختبار التراجع (Regression Test Unit)
def run_regression_test():
    sample_data = {
        'n_w1': 3, 'p_w1': 200000, 'w1_p': 500, 'w1_c': 100, 'w1_d': 10,
        'n_w2': 2, 'p_w2': 300000, 'w2_p': 700, 'w2_c': 150, 'w2_d': 5,
        'n_dr': 3, 'p_dr': 150000, 'd_up': 100, 'd_ua': 2.0,
        'd_pm': 30, 'sal': 40000, 'f_ex': 15000, 'other_inv': 100000, 'dep_years': 5
    }
    res = calculate_financials(sample_data)
    # فحص دقة حساب الاستثمار: (3*200)+(2*300)+(3*150)+100 = 600+600+450+100 = 1750000
    if res["total_inv"] == 1750000:
        return True
    return False

# 4. إدارة البيانات (Persistence Layer)
DB_FILE = "laundry_v8.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
    conn.close()

init_db()

# قيم افتراضية (بناءً على طلبك السابق 50/70 دج)
DEFAULTS = {
    'n_w1': 3, 'p_w1': 180000, 'w1_p': 50, 'w1_c': 110, 'w1_d': 12,
    'n_w2': 2, 'p_w2': 320000, 'w2_p': 70, 'w2_c': 180, 'w2_d': 8,
    'n_dr': 3, 'p_dr': 150000, 'd_up': 100, 'd_ua': 2.0,
    'd_pm': 30, 'sal': 35000, 'f_ex': 10000, 'other_inv': 200000, 'dep_years': 5
}

# --- واجهة المستخدم (Sidebar) ---
with st.sidebar:
    st.title("🛡️ كواليس المشروع")
    st.info("الإصدار: v8.0 (النسخة المستقرة)")
    
    if run_regression_test():
        st.success("✅ اختبار التراجع: سليم")
    else:
        st.error("❌ خطأ في المحرك الحسابي!")
        
    if st.button("🗑️ تصفير شامل للنظام"):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("DELETE FROM settings")
        conn.commit()
        st.rerun()

# --- واجهة المستخدم (الرئيسية) ---
st.title("🚀 محاكي المغسلة الذكية - لوحة PO")

tab1, tab2 = st.tabs(["📊 المدخلات والحسابات", "📈 التحليل الاستراتيجي"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.expander("🏗️ إعدادات الأصول والاستثمار", expanded=True):
            a, b, c = st.columns(3)
            n_w1 = a.number_input("غسالات 12kg", value=DEFAULTS['n_w1'])
            p_w1 = a.number_input("سعر الوحدة (دج)", value=DEFAULTS['p_w1'], key="p1")
            n_w2 = b.number_input("غسالات 18kg", value=DEFAULTS['n_w2'])
            p_w2 = b.number_input("سعر الوحدة (دج) ", value=DEFAULTS['p_w2'], key="p2")
            n_dr = c.number_input("مجففات الغاز", value=DEFAULTS['n_dr'])
            p_dr = c.number_input("سعر المجفف (دج)", value=DEFAULTS['p_dr'], key="p3")

    # تجميع البيانات للحساب
    current_data = {
        'n_w1': n_w1, 'p_w1': p_w1, 'w1_p': st.number_input("سعر الغسلة 12kg", 10, 2000, 50), 
        'w1_c': 110, 'w1_d': st.slider("زبائن 12kg يومياً", 0, 50, 12),
        'n_w2': n_w2, 'p_w2': p_w2, 'w2_p': st.number_input("سعر الغسلة 18kg", 10, 3000, 70),
        'w2_c': 180, 'w2_d': st.slider("زبائن 18kg يومياً", 0, 50, 8),
        'n_dr': n_dr, 'p_dr': p_dr, 'd_up': 100, 'd_ua': 2.0,
        'd_pm': 30, 'sal': 35000, 'f_ex': 10000, 'other_inv': 200000, 'dep_years': 5
    }
    
    fin = calculate_financials(current_data)
    
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي الاستثمار", f"{fin['total_inv']:,} دج")
    
    # تنبيه ذكي بخصوص الأصفار
    if fin['net_profit'] <= 0:
        m2.metric("صافي الربح", "خسارة!", delta=f"{fin['net_profit']:,} دج", delta_color="inverse")
        st.warning("⚠️ تنبيه PO: التكاليف التشغيلية والإهلاك تتجاوز أرباحك. تحتاج لرفع الأسعار أو زيادة الزبائن.")
    else:
        m2.metric("صافي الربح الشهري", f"{fin['net_profit']:,} دج")
        m3.metric("نقطة التعادل", f"{fin['break_even']} غسلة/شهر")

with tab2:
    st.subheader("📈 تحليل الاستدامة المالية")
    
    # رسم بياني لنقطة التعادل
    labels = ['المصاريف الثابتة', 'الأرباح التشغيلية المتوقعة']
    values = [fin['fixed_costs'], max(0, fin['net_profit'] + fin['fixed_costs'])]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(title_text="مقارنة المصاريف بالأرباح")
    st.plotly_chart(fig)

    st.info(f"💡 لكي تبدأ بجني الأرباح، يجب أن يتجاوز عدد الغسلات الشهري {fin['break_even']} غسلة.")
