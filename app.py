"""
Streamlit Web Dashboard for Workforce Promotion & Career Stagnation Analysis.
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
        <div style="font-size: 1.05rem; font-weight: 600; color: #F8FAFC;">Career Analytics</div>
        <div style="font-size: 0.78rem; color: #94A3B8;">Palo Alto Networks Dataset</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 6px;'>Dashboard Views</div>", unsafe_allow_html=True)
    selected_module = st.radio(
        "Navigation",
        [
            "Overview & Key Metrics",
            "Employee Clusters & Segments",
            "Promotion Gap & Stagnation",
            "Retention Action Queue",
            "Managerial Continuity",
            "Career Scenario Simulator",
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
    selected_stage = st.selectbox("Tenure Stage", stages, index=0)

    # Cluster filter
    available_clusters = sorted(df['CareerCluster'].unique().tolist())
    selected_clusters = st.multiselect("Employee Clusters", options=available_clusters, default=[])

    # Stagnation score filter
    min_risk_threshold = st.slider("Minimum Stagnation Risk Score", 0, 100, 0, step=5)


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


# View 1: Overview & Key Metrics
if selected_module == "Overview & Key Metrics":
    render_header(
        title="Workforce & Retention Summary",
        subtitle="Key metrics on promotion delays, stagnation risk, and retention priorities.",
        tag="Overview"
    )

    kpis = get_executive_kpis(filtered_df)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("Total Headcount", f"{kpis['total_employees']:,}", f"{kpis['active_employees']} Active", "#38BDF8")
    with c2:
        render_metric_card("High Stagnation Risk", f"{kpis['high_promo_risk_pct']}%", f"{kpis['high_promo_risk']} Employees", "#FB7185")
    with c3:
        render_metric_card("Retention Priority Queue", f"{kpis['immediate_roi_interventions']}", f"{kpis['immediate_roi_pct']}% of Active Team", "#FBBF24")
    with c4:
        render_metric_card("Avg Promotion Gap", f"{kpis['avg_years_without_promo']} yrs", "Time Since Last Promo", "#818CF8")
    with c5:
        render_metric_card("Historical Attrition", f"{kpis['attrition_rate']}%", "Overall Turnover", "#94A3B8")

    st.markdown("<br/>", unsafe_allow_html=True)

    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Employee Clusters by Stagnation Risk Level</div>", unsafe_allow_html=True)
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
        <strong>Key Insight:</strong> <strong>{high_urgency_count} active employees</strong> with strong performance ratings are experiencing promotion delays. Conducting timely career check-ins can help retain this talent.
    </div>
    """, unsafe_allow_html=True)


# View 2: Employee Clusters & Segments
elif selected_module == "Employee Clusters & Segments":
    render_header(
        title="Employee Clustering & Segments",
        subtitle="Unsupervised K-Means clustering ($K=5$) grouping employees by tenure, promotion gaps, and role duration.",
        tag="Clustering"
    )

    tab_map, tab_comparison = st.tabs([
        "2D Cluster Map (PCA)",
        "Cluster Comparison & Details"
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


# View 3: Promotion Gap & Stagnation
elif selected_module == "Promotion Gap & Stagnation":
    render_header(
        title="Promotion Gap & Role Stagnation",
        subtitle="Examining promotion latencies and role tenure across departments and job roles.",
        tag="Stagnation Analysis"
    )

    col_gap_1, col_gap_2 = st.columns([6, 4])

    with col_gap_1:
        st.plotly_chart(create_stagnation_heatmap(filtered_df), use_container_width=True)

    with col_gap_2:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Distribution of Years Since Last Promotion</div>", unsafe_allow_html=True)
        st.plotly_chart(create_promotion_distribution_chart(filtered_df), use_container_width=True)

    st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin: 16px 0 8px 0;'>Department & Role Breakdown</div>", unsafe_allow_html=True)
    stagnation_matrix = get_role_stagnation_matrix(filtered_df)
    st.dataframe(stagnation_matrix, use_container_width=True, hide_index=True)


# View 4: Retention Action Queue
elif selected_module == "Retention Action Queue":
    render_header(
        title="Retention Priority Queue",
        subtitle="Active high-performing employees experiencing career delays, with suggested action steps.",
        tag="Action Queue"
    )

    action_filter = st.selectbox(
        "Filter by Recommended Action:",
        ["All Actions", "Promotion & Compensation Review", "Lateral Role Rotation", "Upskilling & Training Program", "Manager Mentorship"]
    )

    priority_queue = get_retention_priority_queue(filtered_df, top_n=200)

    if action_filter != "All Actions":
        priority_queue = priority_queue[priority_queue['PrescriptiveAction'].str.contains(action_filter, case=False, na=False)]

    col_q1, col_q2 = st.columns([7, 3])

    with col_q1:
        st.markdown(f"<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Employee Priority List ({len(priority_queue)} candidates)</div>", unsafe_allow_html=True)
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
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Action Breakdown</div>", unsafe_allow_html=True)
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
        label="Download Priority Queue (CSV)",
        data=csv_data,
        file_name="panw_retention_priority_queue.csv",
        mime="text/csv"
    )


# View 5: Managerial Continuity
elif selected_module == "Managerial Continuity":
    render_header(
        title="Managerial Continuity & Impact",
        subtitle="Analyzing the effect of manager tenure and long supervisory continuity on promotions.",
        tag="Team Analysis"
    )

    mgr_matrix = get_manager_insight_matrix(filtered_df)
    st.plotly_chart(create_manager_impact_chart(mgr_matrix), use_container_width=True)

    col_m1, col_m2 = st.columns([5, 5])

    with col_m1:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Stats by Manager Tenure Group</div>", unsafe_allow_html=True)
        st.dataframe(mgr_matrix, use_container_width=True, hide_index=True)

    with col_m2:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Manager Continuity Distribution</div>", unsafe_allow_html=True)
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

    st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin: 18px 0 8px 0;'>Role-Level Manager Tenure Summary</div>", unsafe_allow_html=True)
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


# View 6: Career Scenario Simulator
elif selected_module == "Career Scenario Simulator":
    render_header(
        title="What-If Career Simulator",
        subtitle="Simulate promotions, lateral moves, or training to see how risk scores and career clusters change.",
        tag="Simulator"
    )

    sim_col1, sim_col2 = st.columns([4, 6])

    with sim_col1:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Select Employee Profile</div>", unsafe_allow_html=True)
        sample_emp_ids = filtered_df['EmployeeID'].tolist()
        selected_emp_id = st.selectbox("Select Employee ID", sample_emp_ids, index=0 if sample_emp_ids else None)

        if selected_emp_id:
            emp_row = df[df['EmployeeID'] == selected_emp_id].iloc[0]
            st.markdown(f"""
            <div style="background: #111726; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 12px 14px; margin-bottom: 12px;">
                <div style="font-size: 0.92rem; font-weight: 600; color: #F8FAFC;">{emp_row['EmployeeID']} &mdash; {emp_row['JobRole']}</div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 4px;">Department: {emp_row['Department']} | Level: {emp_row['JobLevel']}</div>
                <div style="font-size: 0.78rem; color: #94A3B8;">Tenure: {emp_row['YearsAtCompany']} yrs | In Current Role: {emp_row['YearsInCurrentRole']} yrs</div>
                <div style="font-size: 0.78rem; color: #94A3B8;">Last Promotion: {emp_row['YearsSinceLastPromotion']} yrs ago | Rating: {emp_row['PerformanceRating']}/4</div>
                <div style="font-size: 0.78rem; color: #38BDF8; margin-top: 4px; font-weight: 500;">Current Cluster: {emp_row['CareerCluster']}</div>
            </div>
            """, unsafe_allow_html=True)

            baseline_dict = emp_row.to_dict()
        else:
            baseline_dict = {
                'TotalWorkingYears': 10, 'YearsAtCompany': 6, 'YearsInCurrentRole': 4,
                'YearsSinceLastPromotion': 4, 'YearsWithCurrManager': 4, 'JobLevel': 2,
                'TrainingTimesLastYear': 2, 'PerformanceRating': 3, 'JobSatisfaction': 3,
                'JobInvolvement': 3, 'Attrition': 0, 'PercentSalaryHike': 14
            }

        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin: 12px 0 6px 0;'>Simulate Intervention</div>", unsafe_allow_html=True)
        sim_action = st.radio(
            "Scenario Preset:",
            ["Manual Sliders", "Promote Employee", "Lateral Role Transfer", "Provide Upskilling Training"]
        )

        if sim_action == "Promote Employee":
            sim_promo_years = 0
            sim_role_years = 0
            sim_job_level = min(int(baseline_dict.get('JobLevel', 1)) + 1, 5)
            sim_trainings = int(baseline_dict.get('TrainingTimesLastYear', 2)) + 1
            sim_salary_hike = int(baseline_dict.get('PercentSalaryHike', 15)) + 8
        elif sim_action == "Lateral Role Transfer":
            sim_promo_years = int(baseline_dict.get('YearsSinceLastPromotion', 2))
            sim_role_years = 0
            sim_job_level = int(baseline_dict.get('JobLevel', 1))
            sim_trainings = int(baseline_dict.get('TrainingTimesLastYear', 2)) + 2
            sim_salary_hike = int(baseline_dict.get('PercentSalaryHike', 15))
        elif sim_action == "Provide Upskilling Training":
            sim_promo_years = int(baseline_dict.get('YearsSinceLastPromotion', 2))
            sim_role_years = int(baseline_dict.get('YearsInCurrentRole', 2))
            sim_job_level = int(baseline_dict.get('JobLevel', 1))
            sim_trainings = 5
            sim_salary_hike = int(baseline_dict.get('PercentSalaryHike', 15))
        else:
            sim_promo_years = st.slider("Years Since Last Promotion", 0, 15, int(baseline_dict.get('YearsSinceLastPromotion', 2)))
            sim_role_years = st.slider("Years in Current Role", 0, 15, int(baseline_dict.get('YearsInCurrentRole', 2)))
            sim_trainings = st.slider("Training Sessions Attended", 0, 6, int(baseline_dict.get('TrainingTimesLastYear', 2)))
            sim_job_level = st.slider("Job Level", 1, 5, int(baseline_dict.get('JobLevel', 1)))
            sim_salary_hike = st.slider("Salary Hike (%)", 0, 35, int(baseline_dict.get('PercentSalaryHike', 15)))

    with sim_col2:
        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Simulated Outcome</div>", unsafe_allow_html=True)
        
        simulated_payload = {
            **baseline_dict,
            'YearsSinceLastPromotion': sim_promo_years,
            'YearsInCurrentRole': sim_role_years,
            'TrainingTimesLastYear': sim_trainings,
            'JobLevel': sim_job_level,
            'PercentSalaryHike': sim_salary_hike
        }

        pred_res = ml_model.predict_single(simulated_payload)

        orig_risk = float(baseline_dict.get('PromotionGapRiskScore', 50.0))
        new_risk = float(pred_res['PromotionGapRiskScore'])
        risk_diff = new_risk - orig_risk

        orig_roi = float(baseline_dict.get('RetentionOpportunityIndex', 60.0))
        new_roi = float(pred_res['RetentionOpportunityIndex'])

        r1, r2, r3 = st.columns(3)
        with r1:
            render_metric_card(
                "Stagnation Risk",
                f"{new_risk:.1f}",
                f"{risk_diff:+.1f} vs Baseline",
                "#34D399" if new_risk < 35 else "#FB7185"
            )
        with r2:
            render_metric_card(
                "Projected Cluster",
                pred_res['CareerCluster'],
                "New Profile",
                "#38BDF8"
            )
        with r3:
            render_metric_card(
                "Retention Opportunity",
                f"{new_roi:.1f}",
                "Priority Score",
                "#FBBF24"
            )

        st.markdown("<div style='font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin: 16px 0 8px 0;'>Position in Career Space (PCA)</div>", unsafe_allow_html=True)
        fig_sim = px.scatter(
            df,
            x='PCA1',
            y='PCA2',
            color='CareerCluster',
            color_discrete_map={k: COLOR_PALETTE.get(k, '#94A3B8') for k in df['CareerCluster'].unique()},
            opacity=0.35,
            title=""
        )
        
        # Overlay simulated employee position
        fig_sim.add_trace(go.Scatter(
            x=[pred_res['PCA1']],
            y=[pred_res['PCA2']],
            mode='markers+text',
            name='Simulated State',
            text=['Simulated Position'],
            textposition='top center',
            marker=dict(size=12, color='#38BDF8', symbol='diamond', line=dict(width=2, color='#FFFFFF'))
        ))

        fig_sim.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(l=20, r=20, t=20, b=30)
        )
        st.plotly_chart(fig_sim, use_container_width=True)


# View 7: Workforce Dataset Explorer
elif selected_module == "Workforce Dataset Explorer":
    render_header(
        title="Dataset Explorer",
        subtitle="Search, filter, and inspect calculated metrics across the workforce dataset.",
        tag="Data"
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

    st.markdown(f"<div style='font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;'>Showing <strong>{len(display_df)}</strong> records:</div>", unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True)

    csv_export = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data (CSV)",
        data=csv_export,
        file_name="panw_workforce_filtered_data.csv",
        mime="text/csv"
    )
