
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
    #canonical_df = 'canonical_dataset.xlsx'
    coverage_file = 'mock_day1-2_account_coverage.xlsx'
    #canonical_df = pd.read_csv('canonical_dataset.xlsx - Sheet1.csv')
    #canonical_df['order_date'] = pd.to_datetime(canonical_df['order_date']) # Ensure dates are usable
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
    "Canonical Dataset",
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

# --- NEW PAGE: CANONICAL DATASET ---
elif page == "Canonical Dataset":
    st.title("🗂️ Canonical Dataset")
    st.markdown("""""")

    # Load Data directly from Excel
    # Note: Ensure 'openpyxl' is installed in your environment
    canonical_df = pd.read_excel('canonical_dataset.xlsx')
    
    # Ensure date format is correct for time-series analysis
    canonical_df['order_date'] = pd.to_datetime(canonical_df['order_date'])

    # Visuals Row 1: Segment Breakdown and Time Trends
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue by Category")
        cat_rev = canonical_df.groupby('category')['order_value'].sum().reset_index()
        fig_cat = px.bar(cat_rev, x='category', y='order_value', color='category', 
                         text_auto='.2s', title="Spend Distribution by Vertical",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with c2:
        st.subheader("Monthly Revenue Trend")
        # Grouping by Month Start to show continuous velocity
        trend = canonical_df.resample('MS', on='order_date')['order_value'].sum().reset_index()
        fig_trend = px.line(trend, x='order_date', y='order_value', markers=True, 
                            title="Portfolio Sales Velocity")
        st.plotly_chart(fig_trend, use_container_width=True)

    # Visuals Row 2: Profitability and Power Users
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Order Margin Distribution")
        fig_margin = px.histogram(canonical_df, x='margin', title="Profitability Spread",
                                  color_discrete_sequence=['#2ecc71'])
        st.plotly_chart(fig_margin, use_container_width=True)
        
    with c4:
        st.subheader("Top 10 High-Value Accounts")
        top_accs = canonical_df.groupby('account_name')['order_value'].sum().nlargest(10).reset_index()
        fig_top = px.bar(top_accs, x='order_value', y='account_name', orientation='h',
                         title="Core Revenue Drivers", color='order_value', 
                         color_continuous_scale='Viridis')
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)

    # Data Label Legend
    st.divider()
    st.subheader("📘 Data Label Legend")
    cols = st.columns(3)
    cols[0].markdown("- **customer_id**: Unique ID.\n- **account_name**: Business name.\n- **order_id**: Transaction ID.")
    cols[1].markdown("- **order_date**: Purchase date.\n- **order_value**: Revenue amount.\n- **sku**: Product ID.")
    cols[2].markdown("- **category**: Product vertical.\n- **rep_role**: Service tier.\n- **margin**: Net profit.")

    # Interactive Data Explorer
    st.subheader("Raw Data Explorer")
    st.dataframe(canonical_df, use_container_width=True, hide_index=True)
    
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
    st.title("📖 Product 3: Sales Playbooks")
    
    selection = st.selectbox("Select Playbook or Context", [
        "Playbook: Phase 1A (Active/No Coverage)", 
        "Playbook: Phase 1B (Dormant/Recovery)", 
        "Product 0: How Data Shapes Execution"
    ])
    
    if selection == "Playbook: Phase 1A (Active/No Coverage)":
        st.subheader("Sales Playbook: Phase 1A (Active / No Coverage)")
        st.info("**Target Profile:** High-revenue, frequent purchasers who currently lack a dedicated point of contact.\n\n**Strategic Intent:** Engagement & Consistency.")
        
        with st.expander("📞 Call Opening", expanded=True):
            st.markdown("**Script:**")
            st.code("I’m reaching out because I've been reviewing your recent order history. You've been highly active with us lately, and I want to ensure you have a direct point of contact to handle pricing tiers and logistics so you don't have to manage everything through the general portal.")
            st.markdown("**Why This:** Establishes immediate relevance. By citing 'recent order history,' the rep proves they aren't cold calling. It pivots from a 'sales call' to a 'service upgrade.'")

        with st.expander("🔍 Discovery Questions"):
            st.markdown("**Script:**")
            st.code("With your current volume, how are you currently managing lead times for your peak seasons? Are there specific product categories where you're finding it difficult to maintain consistent stock?")
            st.markdown("**Why This:** Shifts the focus to operational friction. Since the account is active, the goal is to find 'invisible' pain points in their buying process that a dedicated rep can solve.")

        with st.expander("🛡️ Objection Handling (Pushback: 'I'm fine using the website.')"):
            st.markdown("**Script:**")
            st.code("The site is great for speed, but it can’t flag upcoming inventory shortages or custom volume discounts before you hit 'buy.' My role is to sit behind the scenes and make sure those manual wins happen for you.")
            st.markdown("**Why This:** Reframe. It doesn't fight their behavior; it adds a layer of value (inventory alerts/custom pricing) that the automated system cannot provide.")

        with st.expander("📈 Cross-Sell Prompt"):
            st.markdown("**Script:**")
            st.code("I noticed your spend is concentrated in [Category A]. Many of our partners at your scale are now pairing those with [Category B] to streamline their shipping. Would it be helpful to see a comparison on those rates?")
            st.markdown("**Why This:** Logic-based expansion. It suggests an adjacent category based on their actual buying scale, framed as a 'streamlining' efficiency.")

        with st.expander("✉️ Follow-Up Email"):
            st.markdown("**Subject:** Direct Contact / [Account Name]")
            st.code("Great speaking today. I've attached my direct line and a quick look at the volume pricing tiers we discussed. I’ll keep an eye on your upcoming [Category A] needs and alert you to any stock shifts.")
            st.markdown("**Why This:** Reinforces the 'direct line' value and demonstrates proactive monitoring.")
        
        st.caption("**Assumptions:** Assumes the customer values speed and inventory reliability over price alone.")

    elif selection == "Playbook: Phase 1B (Dormant/Recovery)":
        st.subheader("Sales Playbook: Phase 1B (Dormant / Revenue Recovery)")
        st.info("**Target Profile:** Historically significant accounts where purchasing has stalled or stopped (180+ days since last order).\n\n**Strategic Intent:** Recovery & Trust.")

        with st.expander("📞 Call Opening", expanded=True):
            st.markdown("**Script:**")
            st.code("I was looking back at your account and realized it's been about nine months since our last project together. I wanted to reconnect to see if your requirements have changed or if there was a gap in our service that caused the shift in your ordering.")
            st.markdown("**Why This:** Radical transparency. Acknowledging the exact timeframe (9 months) shows precision. Asking if there was a 'gap in service' gives the customer permission to air grievances.")

        with st.expander("🔍 Diagnostic Discovery"):
            st.markdown("**Script:**")
            st.code("When you moved your volume away, what was the primary driver? Was it a shift in your project types, or did a competitor offer a specific capability or price point we failed to meet?")
            st.markdown("**Why This:** Diagnostic. The goal is to identify if the leakage was due to price, product, or relationship. This is 'intelligence gathering' more than 'selling.'")

        with st.expander("🛡️ Objection Handling (Pushback: 'We've moved to a different supplier.')"):
            st.markdown("**Script:**")
            st.code("I completely respect that. Suppliers win on different things. If I could sent over a 'win-back' quote on your top three historical items just so you have a baseline for your next RFQ, would you be open to keeping it on file?")
            st.markdown("**Why This:** Acknowledge and Reframe. It accepts the current reality but positions the rep as a 'useful backup' or a price-check benchmark, keeping the door ajar.")

        with st.expander("📈 Evolution/Cross-Sell Prompt"):
            st.markdown("**Script:**")
            st.code("Since we last worked together, we’ve overhauled our [Category C] offerings. Based on your previous specs, these might actually solve the [Old Pain Point] we discussed last year.")
            st.markdown("**Why This:** Shows evolution. It gives the customer a reason to look at the company again by highlighting that 'things have changed' since they left.")

        with st.expander("✉️ Follow-Up Email"):
            st.markdown("**Subject:** Following up / Re-establishing our partnership")
            st.code("Thanks for the feedback today. I've noted your comments regarding [Specific Reason for Leaving]. I’ve attached a custom catalog with our updated 2024 specs and pricing. I'd love the chance to quote your next project, even just as a second opinion.")
            st.markdown("**Why This:** Execution discipline. It proves the rep listened to the reason they left and offers a low-pressure way to re-engage.")

        st.caption("**Assumptions:** Assumes churn was due to a specific addressable event (service, price, or product gap) rather than the account closing permanently.")

    elif selection == "Product 0: How Data Shapes Execution":
        st.subheader("How Product 0 Shapes This Content")
        st.markdown("""
        * **Status-Driven Tone:** Phase 1A uses a 'congratulatory/service' tone because the data shows they are active. Phase 1B uses a 'humble/diagnostic' tone because the data shows they are dormant.
        * **Urgency Mapping:** The Phase 1A playbook focuses on securing revenue that is already there but undefended (No Coverage). The Phase 1B playbook focuses on discovering why revenue was lost.
        * **Data-Backed Openers:** Both playbooks use specific data points (order frequency vs. days since last order) to eliminate the 'cold' feel of the call and establish immediate authority.
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
