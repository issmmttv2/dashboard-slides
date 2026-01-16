
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION & PAGE STYLE ---
st.set_page_config(page_title="Product Zero | Sales Strategy", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    .legend-box { padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 10px; border-left: 5px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # 1. Main Strategy Workbook
    strategy_file = 'Mock-productzero-sheet 2.xlsx'
    overview = pd.read_excel(strategy_file, sheet_name='Executive_Overview')
    actions = pd.read_excel(strategy_file, sheet_name='Account_Action_List')
    logic = pd.read_excel(strategy_file, sheet_name='ROI_Logic_Explained')
    summary = pd.read_excel(strategy_file, sheet_name='Phase_Summary')
    
    # 2. Coverage Workbook (Mock day1-2)
    coverage_file = 'mock_day1-2_account_coverage.xlsx'
    # Reading from sheet 'in' as per your file name
    coverage = pd.read_excel(coverage_file, sheet_name='in')
    
    # 3. Generated Leakage Files (CSVs)
    leakage = pd.read_csv('revenue_leakage_detector.csv')
    next_call = pd.read_csv('next_best_call_list.csv')
    
    return overview, actions, logic, summary, coverage, leakage, next_call

try:
    overview_df, action_df, logic_df, summary_df, coverage_df, leakage_df, next_call_df = load_data()
except Exception as e:
    st.error(f"Error loading files. Ensure filenames match exactly on GitHub. Error: {e}")
    st.stop()


# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🛠 Navigation")
page = st.sidebar.radio("Go to", [
    "Executive Summary",
    "Product 0: Phase Deep-Dives",
    "Product 1: Coverage Analyzer", 
    "Product 2: Leakage Detector", 
    "Product 3: Playbooks",
    "Strategy & ROI Logic"
])

# --- PAGE 1: EXECUTIVE SUMMARY ---
if page == "Executive Summary":
    st.title("🚀 Strategy Overview")
    st.markdown("#### *Data-Driven Sales Prioritization Engine*")
    
    # Writeup on the Products
    st.info("""
    **System Overview**
    - **Product 0 (The Brain):** Analyzes historical data to prioritize accounts based on recovery speed.
    - **Product 1 (Coverage):** Audits whether current sales assignments match account potential.
    - **Product 2 (Leakage):** Identifies accounts where ordering frequency has dropped before revenue disappears.
    - **Product 3 (Execution):** Provides specific guidance for calls and emails to drive action.
    """)

    # Phase Definitions
    with st.expander("🔍 Understanding the Phases"):
        st.markdown("""
        - **Phase 1A (Active / No Coverage):** Highest priority. Customers are buying but have no rep. Immediate risk of neglect.
        - **Phase 1B (Dormant / Declining):** Strategic recovery. Customers have slowed down or stopped buying recently.
        - **Phase 2 (Consistent Performers):** High-revenue backbone. Ensure stable maintenance and relationship management.
        - **Phase 3 (Long Tail):** Low-value or stable small accounts. Managed through digital channels or lower-touch inside sales.
        """)

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    # Total Portfolio Value
    portfolio_val = overview_df[overview_df['Metric'] == 'Total Revenue']['Value'].values[0]
    # Target Opps
    target_opps = overview_df[overview_df['Metric'] == 'Phase 1A + 1B Combined Opportunity']['Value'].values[0]
    # Active Accounts
    total_accs = overview_df[overview_df['Metric'] == 'Total Accounts']['Value'].values[0]

    m1.metric("Total Portfolio Value", portfolio_val)
    m2.metric("Priority Opportunities", target_opps)
    m3.metric("Avg ROI Score", round(action_df['roi_speed_score'].mean(), 1))
    m4.metric("Total Accounts", total_accs)
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue Potential by Phase")
        fig_rev = px.bar(summary_df, x='recommended_phase', y='total_revenue', 
                         color='recommended_phase', text_auto='.2s',
                         labels={'total_revenue': 'Total Revenue ($)', 'recommended_phase': 'Phase'},
                         color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_rev, use_container_width=True)
        st.caption("**Legend:** Bars show total historical revenue footprint for each phase segment.")
        
    with c2:
        st.subheader("Account Distribution")
        fig_pie = px.pie(action_df, names='recommended_phase', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.caption("**Legend:** Proportional split of total account count across the four strategic phases.")

# --- PAGE 2: PRODUCT 1 (COVERAGE) ---
elif page == "Product 1: Coverage Analyzer":
    st.title("🎯 Product 1: Account Coverage Gap Analyzer")
    
    st.markdown("""
    **Purpose:** Identify where sales resource allocation is out of sync with account potential.
    """)
    
    with st.expander("📋 Coverage Audit Report (Insights)"):
        st.markdown("""
        - **Unprotected Revenue:** Phase 1A accounts have zero rep coverage despite high activity.
        - **Misallocated Capacity:** High-cost field reps are often stuck on Phase 3 (low-value) stable accounts.
        - **Ghost Coverage:** Many Phase 1B accounts are assigned to reps but continue to decline, suggesting inaction.
        - **Opportunity:** Shifting low-value work away from field sales creates capacity for Phase 1A and 2 recovery.
        """)

    st.markdown("""
    <div class='legend-box'>
    <strong></strong><br>
    ✅ <strong>Aligned:</strong> Role matches account potential.<br>
    ❌ <strong>No Coverage:</strong> High-value account with no assigned rep.<br>
    ⚠️ <strong>Misaligned:</strong> Rep role is either too high-cost for the value (Over-serviced) or too low-touch (Under-serviced).
    </div>
    """, unsafe_allow_html=True)

    # Display Coverage List
    st.subheader("Account Coverage Mapping")
    st.dataframe(coverage_df[['customer_id', 'recommended_phase', 'roi_speed_score', 'rep_role', 'coverage_flag']], use_container_width=True, hide_index=True)
    
    st.markdown("""
    **How it's done:** We compare the ROI score and Phase (potential) against the actual Rep Role assigned.
    **Why it matters:** Ensuring the right person is talking to the right customer at the right time.
    """)

# --- PAGE 3: PRODUCT 2 (LEAKAGE) ---
elif page == "Product 2: Leakage Detector":
    st.title("📉 Product 2: Revenue Leakage Detector")
    
    st.markdown("""
    **Purpose:** Spotting silent attrition by identifying drops in order frequency before accounts go dormant.
    """)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("How & Why")
        st.markdown("""
        - **How:** We flag any account where the order frequency drops by 25% or more compared to their historical baseline.
        - **Why:** Revenue doesn't usually vanish overnight; it fades. Detecting frequency drops is the early warning system.
        """)
    with c2:
        st.subheader("Assumptions")
        st.markdown("""
        - Baseline frequency is calculated over a 12-month trailing period.
        - Recoverable revenue assumes a return to historical ordering patterns.
        """)

    st.subheader("Next Best Call List (Top Recovery Targets)")
    st.dataframe(next_call_df[['account_name', 'reason', 'est_recoverable_revenue']], use_container_width=True, hide_index=True)

    st.subheader("Full Leakage Audit")
    st.dataframe(leakage_df, use_container_width=True, hide_index=True)

# --- PAGE 4: PRODUCT 3 (PLAYBOOKS) ---
elif page == "Product 3: Playbooks":
    st.title("📖 Product 3: Sales Playbook Logic")
    
    selection = st.selectbox("Select Playbook or Context", ["Playbook: Phase 1A (Active/No Coverage)", "Playbook: Phase 1B (Dormant/Recovery)", "The Role of Product 0"])
    
    if selection == "Playbook: Phase 1A (Active/No Coverage)":
        st.subheader("Strategic Intent: Engagement & Consistency")
        st.markdown("""
        **Call Opening:** I noticed your account has been highly active, and I’m reaching out to ensure you have a direct point of contact for pricing and logistics.
        
        **Discovery Questions:** How are you managing lead times for peak seasons? Are there specific categories where you need more stock consistency?
        
        **Objection Handling:** (If they prefer the website) The site is great for speed, but I can flag inventory shortages or volume discounts before you hit 'buy.'
        
        **Follow-Up Email:** Great speaking. I've attached my direct line and the volume pricing tiers we discussed.
        """)
        st.caption("**Assumptions:** Assumes the customer values speed and inventory reliability over price alone.")

    elif selection == "Playbook: Phase 1B (Dormant/Recovery)":
        st.subheader("Strategic Intent: Recovery & Trust")
        st.markdown("""
        **Call Opening:** It’s been about nine months since our last project. I wanted to check in to see if your requirements changed or if we missed a beat on service.
        
        **Discovery Questions:** When you moved your volume away, what was the driver? Was it price, lead time, or a shift in project types?
        
        **Objection Handling:** (If they use a competitor) I respect that. If I could provide a 'win-back' quote for your top items just for your baseline, would that be useful?
        
        **Follow-Up Email:** Thanks for the feedback. I've noted your points and attached our updated 2024 catalog for a second opinion.
        """)
        st.caption("**Assumptions:** Assumes there was a specific reason for departure that can be diagnosed.")

    elif selection == "The Role of Product 0":
        st.subheader("How Product 0 Shapes Execution")
        st.markdown("""
        Product 0 provides the **Context** (Account Status), **Priority** (ROI Score), and **Reasoning** (Why they are in this phase).
        
        This allows us to:
        1. **Match Tone to Status:** Use a service tone for active accounts and a diagnostic tone for dormant ones.
        2. **Focus Questions:** Ask about 'growth' for 1A and 'reasons for leaving' for 1B.
        3. **Sequence Effort:** Reps only see the playbooks for accounts with high ROI scores first.
        """)

# --- PAGE 5: PHASE DEEP-DIVES ---
elif page == "Product 0: Phase Deep-Dives":
    st.title("📂 Execution Lists by Phase")
    
    st.markdown("""
    <div class='legend-box'>
    <strong></strong><br>
    - <strong>ROI Speed Score:</strong> 0-100 scale predicting how fast revenue can be recovered.<br>
    - <strong>Recommended Action:</strong> The primary objective for this account segment.
    </div>
    """, unsafe_allow_html=True)

    selected_phase = st.selectbox("Select Strategy Phase", ['Phase 1A', 'Phase 1B', 'Phase 2', 'Phase 3'])
    
    phase_data = action_df[action_df['recommended_phase'] == selected_phase].sort_values('roi_speed_score', ascending=False)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader(f"Target Accounts: {selected_phase}")
        st.dataframe(phase_data[['account_name', 'account_status', 'roi_speed_score', 'primary_reason']], use_container_width=True)
    
    with col_b:
        st.metric("Phase Account Count", len(phase_data))
        st.markdown(f"**Objective:** {phase_data['recommended_action'].iloc[0] if not phase_data.empty else 'N/A'}")
        
        # Why logic
        st.markdown("**Why this phase?**")
        if selected_phase == 'Phase 1A':
            st.write("High activity but undefended revenue. These accounts represent immediate risk and immediate opportunity.")
        elif selected_phase == 'Phase 1B':
            st.write("Recent churn or dormancy. The goal is to diagnose why they left and offer a reason to return.")
        elif selected_phase == 'Phase 2':
            st.write("The core business. Maintain high-touch relationships to prevent these from falling into Phase 1B.")
        else:
            st.write("Low potential or stable small accounts. Monitor through automated or low-touch channels.")

        csv = phase_data.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export List to CSV", data=csv, file_name=f"{selected_phase}_list.csv")

# --- PAGE 6: STRATEGY & ROI LOGIC ---
elif page == "Strategy & ROI Logic":
    st.title("🎯 The 'How' and 'Why'")
    
    st.subheader("Scoring Weights (The How)")
    st.table(logic_df)
    
    st.subheader("Priority Clustering (The Why)")
    st.markdown("**Legend:** Larger bubbles indicate higher ROI speed scores. High-priority accounts (top-right) represent the fastest path to revenue recovery.")
    fig_scatter = px.scatter(action_df, x='roi_speed_score', y='priority_label', 
                             color='recommended_phase', size='roi_speed_score',
                             hover_name='account_name', title="Opportunity Heatmap",
                             labels={'roi_speed_score': 'ROI Speed Score', 'priority_label': 'Priority Label'})
    st.plotly_chart(fig_scatter, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("Product Zero Dashboard v1.1 | Execution Framework")
