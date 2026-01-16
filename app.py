
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
    "Top 10 Hit List",
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
# --- PAGE 2: TOP 10 HIT LIST ---
elif page == "Top 10 Hit List":
    st.title("🏆 High-Velocity Top 10")
    st.info("These accounts represent the highest recovery potential. Focus resources here for immediate impact.")
    
    top_10 = action_df.sort_values(by='roi_speed_score', ascending=False).head(10)
    
    # Highlight Table
    st.dataframe(top_10[['account_name', 'roi_speed_score', 'recommended_phase', 'recommended_action', 'primary_reason']], 
                 use_container_width=True, hide_index=True)
    
    # Speed Score Chart
    fig_top = px.bar(top_10, x='roi_speed_score', y='account_name', orientation='h',
                     color='roi_speed_score', color_continuous_scale='Greens',
                     title="Top 10 Speed Scores (0-100)")
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)
    
# --- PAGE 3: PRODUCT 2 (LEAKAGE) ---
elif page == "Product 2: Leakage Detector":
    st.title("📉 Product 2: Revenue Leakage Detector")
    
    st.markdown("""
    **Purpose:** Spotting silent attrition by identifying drops in order frequency before accounts go dormant.
    """)
    st.markdown("""
    *Purpose:* Spotting silent attrition by identifying drops in order frequency before accounts go dormant.
    """)

    # --- STRATEGIC INSIGHTS SECTION ---
    st.subheader("Revenue Leakage: Strategic Insights")
    
    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        st.info("""
        *🔍 Silent Attrition*
        Several high-value accounts remain “Active” on paper but have seen a *50%+ drop* in order frequency. This is a leading indicator of churn where the customer is likely shifting volume to a competitor.
        """)
        st.info("""
        *🎯 Concentrated Risk*
        Leakage is often concentrated in specific product categories, suggesting a targeted competitive play that needs to be addressed with specific product-led playbooks.
        """)

    with col_ins2:
        st.info("""
        *💰 The Frequency-Revenue Gap*
        Stabilizing frequency across the top 20 leaking accounts represents a significant recovery opportunity, estimated at *over $200k* in this specific dataset.
        """)
        st.info("""
        *🛡️ Early Warning System*
        By detecting frequency drops at the *25% threshold*, sales can intervene weeks or months before an account officially becomes “Declining” or “Dormant.”
        """)

    st.divider()
    
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
# --- PAGE 4: PRODUCT 3 (PLAYBOOKS) ---
elif page == "Product 3: Playbooks":
    st.title("📖 Product 3: Sales Playbooks")
    
    selection = st.selectbox("Select Playbook or Context", [
        "Playbook: Phase 1A (Active/No Coverage)", 
        "Playbook: Phase 1B (Dormant/Recovery)", 
        "Product 0: How Data Shapes Execution"
    ])
    
    if selection == "Playbook: Phase 1A (Active/No Coverage)":
        st.subheader("Strategy: The Service Upgrade (Active / No Coverage)")
        st.info("**Intent:** Transition transactional web-buyers into managed accounts to prevent shopping around.")
        
        # 1. Call Opening
        st.markdown("### 1. Call Opening")
        st.success("“I’m calling from the Account Strategy team. I was reviewing your account activity—specifically your consistent orders in [Category]—and I realized that despite your volume, you don't currently have a dedicated specialist assigned to you. I’m calling to bridge that gap and ensure you have a direct line for project pricing and inventory flags.”")
        st.caption("**The Logic:** Links call to actual behavior. Pivots from 'sales' to a 'service upgrade.'")

        # 2. Discovery Questions
        st.markdown("### 2. Discovery Questions")
        st.success("“Since you’re currently placing these orders through the portal, what is the one thing about our lead-time communication that slows your team down? Also, who else on your team is authorized to pull technical specs? I want to make sure they have the same direct access I'm providing you.”")
        st.caption("**The Logic:** Uncovers changes in needs and identifies other stakeholders (Expansion).")

        # 3. Objection Handling
        st.markdown("### 3. Objection Handling (Pushback: 'We're all set/The website is fine')")
        st.success("“I’m glad the portal is working well—it’s designed for speed. My goal isn’t to change HOW you buy, but to change WHAT you pay. I can flag volume discounts or stock shortages before you even hit 'checkout' on the site.”")
        st.caption("**The Logic:** Acknowledge → Reframe. Adds a layer of value the automated system cannot provide.")

        # 4. Cross-Sell Prompt
        st.markdown("### 4. Cross-Sell Prompt")
        st.success("“Most clients moving your volume of [Primary Category] are also seeing a 15% savings by bundling their [Adjacent Category] requirements. Would you like a price-comparison on your next bundle?”")
        st.caption("**The Logic:** Logic-based expansion framed as 'streamlining' efficiency.")

        # 5. Follow-Up Email
        st.markdown("### 5. Follow-Up Email")
        st.success("**Subject:** Direct Contact for [Account Name] | Project Pricing\n\n“Great speaking today. I’ve attached my direct line and a summary of the volume pricing tiers for [Category] we talked about. Next time you have a project over $5k, shoot me the SKU list before you buy so I can check for additional savings.”")
        
        st.divider()
        st.markdown("**Note for Reps:** This account is active but undefended. Focus on engagement and consistency.")

    elif selection == "Playbook: Phase 1B (Dormant/Recovery)":
        st.subheader("Strategy: The Diagnostic Recovery (Dormant / Declined)")
        st.info("**Intent:** Re-engage historically significant accounts by uncovering the 'Silent No' (the reason they left).")

        # 1. Call Opening
        st.markdown("### 1. Call Opening")
        st.warning("“I was looking at your historical project history and noticed a significant shift. We used to partner closely on [Category] projects, but it’s been about nine months since our last order. Usually, when a partner of your size stops ordering, it’s because we either missed a beat on service or a competitor moved the goalposts. I’m calling to see which one it was.”")
        st.caption("**The Logic:** Radical transparency. Acknowledges the gap in time to build immediate trust.")

        # 2. Discovery Questions
        st.markdown("### 2. Diagnostic Discovery")
        st.warning("“When you moved that volume away, was it driven by a specific service failure, or did a competitor offer a specific capability we were lacking? If I could provide a 'shadow quote' on your next project—just to give you a baseline to keep your current supplier honest—would you be open to that?”")
        st.caption("**The Logic:** Diagnostic focus. Intelligence gathering over selling.")

        # 3. Objection Handling
        st.markdown("### 3. Objection Handling (Pushback: 'We have a new supplier')")
        st.warning("“I respect that. Stability is important. I’m not asking you to fire them; I’m asking to be your 'Plan B.' If they have a stock-out or a price hike, you shouldn't have to start from scratch. Let’s keep your account active as a safety net.”")
        st.caption("**The Logic:** Acknowledge and Reframe. Positions the rep as a useful 'Plan B' backup.")

        # 4. Evolution/Cross-Sell Prompt
        st.markdown("### 4. Evolution Prompt")
        st.warning("“Since we last worked together, we’ve overhauled our [New Product Line]. Based on your previous specs, these might actually solve the [Old Pain Point] we discussed last year. Would you like the new spec sheet?”")
        st.caption("**The Logic:** Shows 'things have changed' since they left, giving them a reason to look again.")

        # 5. Follow-Up Email
        st.markdown("### 5. Follow-Up Email")
        st.warning("**Subject:** Following up / Project History [Account Name]\n\n“Thanks for the candid feedback. I've noted your comments regarding [Reason for Leaving]. I’ve attached our updated 2024 catalog. Even if you're set with your current supplier, I'd appreciate the chance to bid on your next 'rush' order just to show you the improvements we've made.”")

        st.divider()
        st.markdown("**Note for Reps:** This account requires re-engagement. Focus on recovery and trust-building.")

    elif selection == "Product 0: How Data Shapes Execution":
        st.subheader("Why Product Zero Inputs Matter")
        st.markdown("""
        The Product Zero "Brain" provides the **Context** (Status) and **Priority** (ROI Score) so reps don't have to guess how to start the call.
        
        * **Phase 1A (Active):** Uses a **Service Tone**. The data shows they are spending, so we focus on *friction removal* and *retention*.
        * **Phase 1B (Dormant):** Uses a **Diagnostic Tone**. The data shows they *stopped* spending, so we focus on *recovery* and *learning why*.
        * **Relevance:** Both playbooks use "Behavior-Based Openers" (past purchases or time gaps) to ensure the rep sounds like a partner, not a cold-caller.
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
# --- PAGE 6: STRATEGY & ROI LOGIC ---
elif page == "Strategy & ROI Logic":
    st.title("🎯 The 'How' and 'Why': Logic & Formulas")
    st.markdown("""
    This section documents the mathematical framework used to prioritize accounts. 
    Product Zero uses these formulas to remove subjectivity from sales assignments.
    """)

    # 1. ROI Speed Score
    st.subheader("1. ROI Speed Score Calculation")
    st.markdown("""
    The ROI Speed Score predicts how fast revenue can be recovered or stabilized. 
    It is a weighted average of three normalized variables:
    """)
    st.latex(r"ROI = (Recent\_Activity \times 0.4) + (Historical\_Revenue \times 0.4) + (Coverage\_Gap \times 0.2)")
    
    with st.expander("Variable Definitions"):
        st.markdown("""
        - **Recent Activity (40%)**: A 0-100 score based on order frequency in the last 90 days. High activity = high score.
        - **Historical Revenue (40%)**: A 0-100 score based on the total Lifetime Value (LTV) of the account.
        - **Coverage Gap (20%)**: A 'low-hanging fruit' bonus. If an account is active but has no rep (Phase 1A), it receives the full 20% weight.
        """)

    # 2. Revenue Leakage: Frequency Drop
    st.subheader("2. Leakage Detector: Frequency Drop %")
    st.markdown("""
    Silent attrition is detected by measuring the decay in ordering patterns compared to a customer's historical baseline.
    """)
    st.latex(r"Frequency\_Drop\,\% = \frac{\text{Baseline Frequency} - \text{Current Frequency}}{\text{Baseline Frequency}}")
    
    with st.expander("Calculation Logic"):
        st.markdown("""
        - **Baseline Frequency**: Average orders per month over the trailing 12 months.
        - **Current Frequency**: Average orders per month over the last 3 months.
        - **The 25% Threshold**: Any account exceeding a 25% drop is automatically flagged for a diagnostic call.
        """)

    # 3. Estimated Recoverable Revenue
    st.subheader("3. Estimated Recoverable Revenue (Annualized)")
    st.markdown("""
    This calculates the dollar value of the 'gap' between a customer's healthy state and their current declining state.
    """)
    st.latex(r"Est.\,Recoverable\,Revenue = (\text{Baseline Monthly Rev} - \text{Current Monthly Rev}) \times 12")
    st.info("**Why 12 months?** Annualizing the loss helps sales managers prioritize a 'consistent leak' over a one-time missed order.")

    # 4. Coverage Gap Analysis (ROI-Based Logic)
    st.subheader("4. Coverage Gap Analysis & Resource Alignment")
    st.markdown("""
    The system identifies gaps by comparing the **ROI Speed Score** (Account Potential) against the 
    **Rep Role** (Resource Cost). A gap is not just "missing" coverage; it is "misaligned" coverage.
    """)

    # Highlighting the ROI connection
    st.info("""
    **The ROI Rule:** - If **ROI Score > 70** and **Rep = None**, it is flagged as a **Phase 1A Critical Gap**.
    - If **ROI Score > 70** and **Rep = Inside**, it is flagged as **Under-Serviced** (needs a Field Rep).
    """)

    # Formulas/Conditions for the Gap
    st.markdown("### Coverage Status Conditions")
    st.markdown(\"\"\"
    | Condition | ROI Threshold | Assigned Role | Condition Met |
    | :--- | :--- | :--- | :--- |
    | **Critical Gap** | > 70 | None | High-potential revenue is undefended. |
    | **Service Gap** | > 60 | Inside Sales | High-potential account is being under-served. |
    | **Efficiency Gap** | < 30 | Outside Sales | High-cost resource is assigned to low-potential account. |
    | **Optimized** | Matches Phase | Correct Tier | Resource is perfectly aligned with ROI speed. |
    \"\"\")

    # Formula for Logic (Pseudo-code)
    st.latex(r"Gap\_Status = \begin{cases} \text{Critical} & \text{if } ROI > 70 \text{ and Rep} = None \\ \text{Misaligned} & \text{if } ROI > 70 \text{ and Rep} = Inside \\ \text{Inefficient} & \text{if } ROI < 30 \text{ and Rep} = Outside \end{cases}")
    # Visualizing the Result
    st.divider()
    st.subheader("Priority Clustering (The Output)")
    st.markdown("**Logic:** The Heatmap below is the visual result of the formulas above. Accounts in the top-right represent the fastest path to revenue.")
    
    fig_scatter = px.scatter(action_df, x='roi_speed_score', y='priority_label', 
                             color='recommended_phase', size='roi_speed_score',
                             hover_name='account_name', title="Opportunity Heatmap",
                             labels={'roi_speed_score': 'ROI Speed Score', 'priority_label': 'Priority Label'})
    st.plotly_chart(fig_scatter, use_container_width=True)

'''
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
    st.plotly_chart(fig_scatter, use_container_width=True)'''

st.sidebar.markdown("---")
st.sidebar.caption("Product Zero Dashboard v1.1 | Execution Framework")
