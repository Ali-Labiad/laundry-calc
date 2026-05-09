import streamlit as st
import matplotlib.pyplot as plt

# 1. Page Configuration & Professional Theme
st.set_page_config(page_title="Laundro-Sim Pro v9.5", layout="wide")

# 2. Financial Engine (Optimized Logic)
def calculate_financials(data):
    # Total Capital Expenditure (CapEx)
    total_inv = (data['wash_12_qty'] * data['price_w12']) + \
                (data['wash_18_qty'] * data['price_w18']) + \
                (data['dryer_qty'] * data['price_dryer']) + \
                data['setup_costs']
    
    # Per-customer Drying Profit: Units * (Unit Price - Energy Cost)
    dry_profit_per_user = data['dry_units_per_user'] * (data['dry_unit_price'] - data['dry_unit_cost'])
    
    # Operation Margins (Service Price + Drying Profit - Detergents - Maintenance)
    maint_buffer = 20 # Fixed maintenance reserve per cycle (DZD)
    margin_w12 = (data['service_p_w12'] + dry_profit_per_user) - (data['detergent_w12'] + maint_buffer)
    margin_w18 = (data['service_p_w18'] + dry_profit_per_user) - (data['detergent_w18'] + maint_buffer)
    
    # Monthly Revenue Calculations
    monthly_gross = ((margin_w12 * data['cust_w12_daily']) + (margin_w18 * data['cust_w18_daily'])) * data['work_days']
    
    # Fixed Costs & Monthly Depreciation
    monthly_depreciation = (total_inv - data['setup_costs']) / (max(data['dep_years'], 1) * 12)
    total_fixed_monthly = data['op_fixed_costs'] + monthly_depreciation
    
    # Final Metrics
    net_profit = monthly_gross - total_fixed_monthly
    avg_margin = (margin_w12 + margin_w18) / 2
    break_even = total_fixed_monthly / avg_margin if avg_margin > 0 else 0
    
    return {
        "total_inv": total_inv,
        "net_profit": int(net_profit),
        "break_even": int(break_even),
        "total_fixed": int(total_fixed_monthly),
        "depreciation": int(monthly_depreciation),
        "dry_revenue_share": int(dry_profit_per_user * (data['cust_w12_daily'] + data['cust_w18_daily']) * data['work_days'])
    }

# --- Interface Setup ---
st.title("📊 Laundro-Sim Pro v9.5")
st.markdown("##### *Professional Investment Dashboard - Algerian Dinar (DZD)*")
st.divider()

# Helper for Currency Formatting
def f_dzd(val): return f"{val:,.0f} DZD"

# --- Main Dashboard Columns ---
col_input, col_output = st.columns([2.2, 1])

with col_input:
    st.subheader("⚙️ Input Parameters")
    
    # Section 1: Asset Investment (CapEx)
    with st.expander("🏗️ 1. Equipment & Setup (Assets)", expanded=True):
        c1, c2, c3 = st.columns(3)
        p_w12 = c1.number_input("Unit Price: Wash 12kg", value=180000, step=5000)
        p_w18 = c2.number_input("Unit Price: Wash 18kg", value=320000, step=5000)
        p_dry = c3.number_input("Unit Price: Dryer", value=150000, step=5000)
        setup = st.number_input("Setup Costs (Plumbing, Decor, Gas)", value=200000, step=10000)

    # Section 2: Service Pricing & Daily Flow
    st.subheader("💰 2. Daily Operations")
    o1, o2 = st.columns(2)
    with o1:
        st.info("Wash 12kg Service")
        p_srv_12 = st.number_input("Service Price", value=50, step=10, key="p12")
        d_cust_12 = st.number_input("Daily Customers", value=12, step=1, key="d12")
    
    with o2:
        st.info("Wash 18kg Service")
        p_srv_18 = st.number_input("Service Price ", value=70, step=10, key="p18")
        d_cust_18 = st.number_input("Daily Customers ", value=8, step=1, key="d18")

    # Section 3: Drying Logic & Fixed Expenses
    st.subheader("🔥 3. Drying Logic & Overhead")
    d1, d2, d3 = st.columns(3)
    dry_up = d1.number_input("Drying Unit Price", value=100, step=10)
    dry_uu = d2.number_input("Avg Units per Wash", value=2.0, step=0.5)
    fix_op = d3.number_input("Rent & Salaries", value=45000, step=1000)

# --- Calculation Trigger ---
data = {
    'wash_12_qty': 3, 'price_w12': p_w12, 'service_p_w12': p_srv_12, 'detergent_w12': 110, 'cust_w12_daily': d_cust_12,
    'wash_18_qty': 2, 'price_w18': p_w18, 'service_p_w18': p_srv_18, 'detergent_w18': 180, 'cust_w18_daily': d_cust_18,
    'dryer_qty': 3, 'price_dryer': p_dry, 'dry_unit_price': dry_up, 'dry_unit_cost': 15, 'dry_units_per_user': dry_uu,
    'work_days': 30, 'op_fixed_costs': fix_op, 'setup_costs': setup, 'dep_years': 5
}

res = calculate_financials(data)

# --- Results Dashboard ---
with col_output:
    st.subheader("📈 Summary Results")
    
    # Net Profit Card
    profit_color = "green" if res['net_profit'] > 0 else "red"
    st.markdown(f"""
    <div style="padding:20px; border-radius:10px; background-color:#f0f2f6; border-left: 8px solid {profit_color};">
        <p style="margin:0; font-weight:bold; color:#31333F;">MONTHLY NET PROFIT</p>
        <h2 style="margin:0; color:{profit_color};">{f_dzd(res['net_profit'])}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("Total Investment", f_dzd(res['total_inv']))
    st.metric("Break-even Point", f"{res['break_even']} Customers/Month")
    st.metric("Monthly Depreciation", f_dzd(res['depreciation']))
    
    st.divider()
    
    # Visual Analytics
    fig, ax = plt.subplots(figsize=(5, 4.5))
    categories = ['Fixed + Depr.', 'Drying Income']
    values = [res['total_fixed'], res['dry_revenue_share']]
    ax.bar(categories, values, color=['#e74c3c', '#2ecc71'])
    ax.set_title("Opex vs. Drying Contribution")
    st.pyplot(fig)

    if res['net_profit'] <= 0:
        st.error("Financial Warning: Revenue is below the total fixed costs. Adjust pricing or increase daily customers.")

st.markdown("---")
st.caption("Developed for Professional Investment Planning | Currency: DZD | Logic: Units-Based Drying")
