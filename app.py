"""
Streamlit Web Dashboard for Workforce Promotion & Career Stagnation Analysis.
Palo Alto Networks Dataset - Unified Mentor Project.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

from src.data_loader import get_full_processed_dataset
from src.ml_pipeline import CareerIntelligenceModel, ARCHETYPE_DESCRIPTIONS, CLUSTERING_FEATURES
from src.analytics import (
    get_executive_kpis, get_role_stagnation_matrix,
    get_manager_insight_matrix, get_retention_priority_queue
)
from src.ui_components import (
    apply_custom_css, render_header, render_metric_card,
    create_pca_scatter_plot, create_cluster_comparison_chart,
    create_stagnation_heatmap, create_promotion_distribution_chart,
    create_manager_impact_chart, COLOR_PALETTE
)

# Page configuration
st.set_page_config(
    page_title="Career & Promotion Analytics | Palo Alto Networks",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS styling
apply_custom_css()


@st.cache_data
def load_and_prepare_data():
    """Loads dataset and fits K-Means clustering model."""
    df = get_full_processed_dataset()
    model = CareerIntelligenceModel(n_clusters=5, random_state=42)
    clustered_df = model.fit_transform_dataset(df)
    return clustered_df, model


# Load data
try:
    df, ml_model = load_and_prepare_data()
except Exception as e:
    st.error(f"Error loading workforce data: {str(e)}")
    st.stop()


# Sidebar Navigation & Filters
with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0 14px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 14px;">
        <div style="font-size: 1.02rem; font-weight: 600; color: #F8FAFC;">Palo Alto Networks</div>
        <div style="font-size: 0.78rem; color: #94A3B8;">Career Progression Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 6px;'>Modules</div>", unsafe_allow_html=True)
    selected_module = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Career Path Clustering Dashboard",
            "Promotion Gap Monitor",
            "Retention Opportunity Panel",
            "Managerial Insight Dashboard",
            "Workforce Dataset Explorer"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<div style='padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.08); margin-top: 14px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 6px;'>Filters</div>", unsafe_allow_html=True)

    # Department filter
    departments = ["All"] + sorted(df['Department'].unique().tolist())
    selected_dept = st.selectbox("Department", departments, index=0)

    # Job Role filter
    available_roles = df['JobRole'].unique().tolist()
    if selected_dept != "All":
        available_roles = df[df['Department'] == selected_dept]['JobRole'].unique().tolist()
    selected_roles = st.multiselect("Job Roles", options=sorted(available_roles), default=[])

    # Cohort filter
    attrition_filter = st.selectbox("Employee Cohort", ["Active Employees Only", "All Employees", "Attrited Only"])

    # Career Stage filter
    stages = ["All"] + sorted(df['CareerStage'].unique().tolist())
    selected_stage = st.selectbox("Career Stage", stages, index=0)

    # Cluster explorer
    available_clusters = sorted(df['CareerCluster'].unique().tolist())
    selected_clusters = st.multiselect("Career Clusters", options=available_clusters, default=[])

    # Stagnation score filter
    min_risk_threshold = st.slider("Promotion Gap Risk Threshold", 0, 100, 0, step=5)


# Apply filtering
filtered_df = df.copy()

if selected_dept != "All":
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]

if selected_roles:
    filtered_df = filtered_df[filtered_df['JobRole'].isin(selected_roles)]

if selected_clusters:
    filtered_df = filtered_df[filtered_df['CareerCluster'].isin(selected_clusters)]

if attrition_filter == "Active Employees Only":
    filtered_df = filtered_df[filtered_df['Attrition'] == 0]
elif attrition_filter == "Attrited Only":
    filtered_df = filtered_df[filtered_df['Attrition'] == 1]

if selected_stage != "All":
    filtered_df = filtered_df[filtered_df['CareerStage'] == selected_stage]

if min_risk_threshold > 0:
    filtered_df = filtered_df[filtered_df['PromotionGapRiskScore'] >= min_risk_threshold]


# Module 0: Executive Overview
if selected_module == "Executive Overview":
    render_header(
        title="Executive Overview",
        subtitle="High-level metrics on career progression, promotion latency, and retention priorities.",
        tag="Overview"
    )

    kpis = get_executive_kpis(filtered_df)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("Total Headcount", f"{kpis['total_employees']:,}", f"{kpis['active_employees']} Active", "#38BDF8")
    with c2:
        render_metric_card("Stagnation Risk", f"{kpis['high_promo_risk_pct']}%", f"{kpis['high_promo_risk']} High-Risk", "#FB7185")
    with c3:
        render_metric_card("Retention Priority", f"{kpis['immediate_roi_interventions']}", f"{kpis['immediate_roi_pct']}% of Active Team", "#FBBF24")
    with c4:
        render_metric_card("Avg Promotion Gap", f"{kpis['avg_years_without_promo']} yrs", "Years Since Promo", "#818CF8")
    with c5:
        render_metric_card("Attrition Rate", f"{kpis['attrition_rate']}%", "Historical Baseline", "#94A3B8")

    st.markdown("<br/>", unsafe_allow_html=True)

    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Career Clusters by Stagnation Risk Level</div>", unsafe_allow_html=True)
        fig_bar = px.histogram(
            filtered_df,
            x='CareerCluster',
            color='PromotionGapRiskLevel',
            barmode='group',
            color_discrete_map={'Low Risk': '#34D399', 'Medium Risk': '#FBBF24', 'High Risk': '#FB7185'},
            title=""
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            xaxis=dict(gridcolor='rgba(255,255,255,0.06)', title=''),
            yaxis=dict(gridcolor='rgba(255,255,255,0.06)', title='Headcount'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(17, 23, 38, 0.8)'),
            margin=dict(l=20, r=20, t=25, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Retention Opportunity by Department</div>", unsafe_allow_html=True)
        dept_risk = filtered_df.groupby('Department')['RetentionOpportunityIndex'].mean().reset_index()
        fig_donut = px.pie(
            dept_risk,
            names='Department',
            values='RetentionOpportunityIndex',
            hole=0.6,
            color='Department',
            color_discrete_sequence=['#38BDF8', '#818CF8', '#34D399'],
            title=""
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(l=20, r=20, t=20, b=30)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    high_urgency_count = len(filtered_df[filtered_df['RetentionPriorityLevel'] == 'Immediate Action'])
    st.markdown(f"""
    <div class="custom-alert">
        <strong>Retention Note:</strong> <strong>{high_urgency_count} active employees</strong> with high performance ratings are currently experiencing extended promotion gaps. Timely internal mobility check-ins can help retain them.
    </div>
    """, unsafe_allow_html=True)


# Module 1: Career Path Clustering Dashboard
elif selected_module == "Career Path Clustering Dashboard":
    render_header(
        title="Career Path Clustering Dashboard",
        subtitle="Unsupervised K-Means clustering ($K=5$) grouping the workforce into interpretable career patterns.",
        tag="Clustering"
    )

    tab_map, tab_comparison = st.tabs([
        "Cluster Distribution (2D PCA)",
        "Career Pattern Summaries"
    ])

    with tab_map:
        st.plotly_chart(create_pca_scatter_plot(filtered_df), use_container_width=True)
        st.caption("2D projection of career features using Principal Component Analysis (PCA).")

    with tab_comparison:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Average Tenures & Promotion Gaps Across Clusters</div>", unsafe_allow_html=True)
        st.plotly_chart(create_cluster_comparison_chart(filtered_df), use_container_width=True)

        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin: 16px 0 8px 0;'>Cluster Descriptions</div>", unsafe_allow_html=True)
        c_cols = st.columns(len(ARCHETYPE_DESCRIPTIONS))
        for col, (arch_name, arch_info) in zip(c_cols, ARCHETYPE_DESCRIPTIONS.items()):
            with col:
                st.markdown(f"""
                <div style="background: #111726; border: 1px solid rgba(255, 255, 255, 0.08); border-top: 3px solid {arch_info['color']}; padding: 10px 12px; border-radius: 6px; height: 100%;">
                    <div style="font-size: 0.82rem; font-weight: 600; color: {arch_info['color']};">{arch_info['badge']}</div>
                    <div style="font-size: 0.76rem; color: #CBD5E1; margin: 6px 0 4px 0;">{arch_info['summary']}</div>
                    <div style="font-size: 0.72rem; color: #94A3B8;"><strong>Action:</strong> {arch_info['strategy']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin: 18px 0 8px 0;'>Cluster Averages Table</div>", unsafe_allow_html=True)
        cluster_summary = filtered_df.groupby('CareerCluster')[['YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion', 'TotalWorkingYears', 'PromotionGapRiskScore']].mean().round(2)
        st.dataframe(cluster_summary, use_container_width=True)


# Module 2: Promotion Gap Monitor
elif selected_module == "Promotion Gap Monitor":
    render_header(
        title="Promotion Gap Monitor",
        subtitle="Identifying high-gap employees and analyzing role-level career stagnation.",
        tag="Promotion Monitor"
    )

    col_gap_1, col_gap_2 = st.columns([6, 4])

    with col_gap_1:
        st.plotly_chart(create_stagnation_heatmap(filtered_df), use_container_width=True)

    with col_gap_2:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Distribution of Years Since Last Promotion</div>", unsafe_allow_html=True)
        st.plotly_chart(create_promotion_distribution_chart(filtered_df), use_container_width=True)

    st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin: 16px 0 8px 0;'>Role-Level Stagnation Breakdown</div>", unsafe_allow_html=True)
    stagnation_matrix = get_role_stagnation_matrix(filtered_df)
    st.dataframe(stagnation_matrix, use_container_width=True, hide_index=True)


# Module 3: Retention Opportunity Panel
elif selected_module == "Retention Opportunity Panel":
    render_header(
        title="Retention Opportunity Panel",
        subtitle="Identifying employees needing career intervention and suggesting tailored actions.",
        tag="Retention Panel"
    )

    action_filter = st.selectbox(
        "Filter by Suggested Action:",
        ["All Actions", "Promotion & Compensation Review", "Lateral Role Rotation", "Upskilling & Training Program", "Manager Mentorship"]
    )

    priority_queue = get_retention_priority_queue(filtered_df, top_n=200)

    if action_filter != "All Actions":
        priority_queue = priority_queue[priority_queue['PrescriptiveAction'].str.contains(action_filter, case=False, na=False)]

    col_q1, col_q2 = st.columns([7, 3])

    with col_q1:
        st.markdown(f"<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Employees Needing Career Intervention ({len(priority_queue)} Total)</div>", unsafe_allow_html=True)
        st.dataframe(
            priority_queue,
            use_container_width=True,
            hide_index=True,
            column_config={
                "RetentionOpportunityIndex": st.column_config.ProgressColumn("Retention Opportunity", min_value=0, max_value=100, format="%.1f"),
                "PromotionGapRiskScore": st.column_config.ProgressColumn("Stagnation Risk", min_value=0, max_value=100, format="%.1f")
            }
        )

    with col_q2:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Suggested Action Breakdown</div>", unsafe_allow_html=True)
        action_counts = priority_queue['PrescriptiveAction'].value_counts().reset_index()
        action_counts.columns = ['PrescriptiveAction', 'Count']
        
        fig_actions = px.pie(
            action_counts,
            names='PrescriptiveAction',
            values='Count',
            hole=0.55,
            color_discrete_sequence=['#38BDF8', '#818CF8', '#FBBF24', '#FB7185', '#34D399'],
            title=""
        )
        fig_actions.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(l=10, r=10, t=10, b=20)
        )
        st.plotly_chart(fig_actions, use_container_width=True)

    csv_data = priority_queue.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Intervention List (CSV)",
        data=csv_data,
        file_name="panw_retention_intervention_queue.csv",
        mime="text/csv"
    )


# Module 4: Managerial Insight Dashboard
elif selected_module == "Managerial Insight Dashboard":
    render_header(
        title="Managerial Insight Dashboard",
        subtitle="Analyzing manager tenure vs career growth and detecting team-level stagnation signals.",
        tag="Managerial Insight"
    )

    mgr_matrix = get_manager_insight_matrix(filtered_df)
    st.plotly_chart(create_manager_impact_chart(mgr_matrix), use_container_width=True)

    col_m1, col_m2 = st.columns([5, 5])

    with col_m1:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Manager Tenure vs Promotion Delay</div>", unsafe_allow_html=True)
        st.dataframe(mgr_matrix, use_container_width=True, hide_index=True)

    with col_m2:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Manager Continuity Categories</div>", unsafe_allow_html=True)
        impact_counts = filtered_df['ManagerStabilityImpact'].value_counts().reset_index()
        impact_counts.columns = ['Category', 'Count']
        fig_mgr_pie = px.pie(
            impact_counts,
            names='Category',
            values='Count',
            color='Category',
            color_discrete_map={
                'Prolonged Stagnant Manager Dyad': '#FB7185',
                'Stable Leadership Continuity': '#34D399',
                'Moderate Manager Continuity': '#818CF8',
                'Recent Manager Transition': '#FBBF24'
            },
            hole=0.55
        )
        fig_mgr_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(l=20, r=20, t=20, b=30)
        )
        st.plotly_chart(fig_mgr_pie, use_container_width=True)

    st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin: 18px 0 8px 0;'>Team-Level Stagnation Signals by Role</div>", unsafe_allow_html=True)
    team_signals = filtered_df.groupby(['Department', 'JobRole']).agg(
        TeamHeadcount=('EmployeeID', 'count'),
        AvgYearsWithManager=('YearsWithCurrManager', 'mean'),
        AvgYearsSincePromotion=('YearsSinceLastPromotion', 'mean'),
        StagnantDyadCount=('ManagerStabilityImpact', lambda s: (s == 'Prolonged Stagnant Manager Dyad').sum()),
        AvgStagnationRisk=('PromotionGapRiskScore', 'mean')
    ).reset_index()
    for col in ['AvgYearsWithManager', 'AvgYearsSincePromotion', 'AvgStagnationRisk']:
        team_signals[col] = team_signals[col].round(1)
    team_signals = team_signals.sort_values(by=['StagnantDyadCount', 'AvgStagnationRisk'], ascending=[False, False])
    st.dataframe(team_signals, use_container_width=True, hide_index=True)


# Module 5: Workforce Dataset Explorer
elif selected_module == "Workforce Dataset Explorer":
    render_header(
        title="Workforce Dataset Explorer",
        subtitle="Search, filter, and export the complete dataset with calculated career metrics.",
        tag="Data Explorer"
    )

    search_query = st.text_input("Search by Employee ID, Department, or Job Role:", "")

    display_df = filtered_df.copy()
    if search_query:
        mask = (
            display_df['EmployeeID'].astype(str).str.contains(search_query, case=False) |
            display_df['Department'].astype(str).str.contains(search_query, case=False) |
            display_df['JobRole'].astype(str).str.contains(search_query, case=False)
        )
        display_df = display_df[mask]

    st.markdown(f"<div style='font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;'>Showing <strong>{len(display_df)}</strong> matching records:</div>", unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True)

    csv_export = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data (CSV)",
        data=csv_export,
        file_name="panw_workforce_filtered_data.csv",
        mime="text/csv"
    )
