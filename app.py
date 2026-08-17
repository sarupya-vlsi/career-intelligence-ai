"""
Palo Alto Networks - Career Intelligence & Retention Opportunity Platform
Main Multi-Module Streamlit Web Application (Clean Enterprise Design)
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
    get_manager_insight_matrix, get_archetype_radar_data,
    get_retention_priority_queue
)
from src.ui_components import (
    apply_custom_css, render_header, render_metric_card,
    create_pca_scatter_plot, create_radar_chart,
    create_stagnation_heatmap, create_manager_impact_chart,
    COLOR_PALETTE
)

# Set page config
st.set_page_config(
    page_title="Career Intelligence Platform | Palo Alto Networks",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Clean Enterprise CSS Theme
apply_custom_css()


@st.cache_data
def load_and_prepare_data():
    """Caches full dataset and fits ML clustering pipeline."""
    df = get_full_processed_dataset()
    model = CareerIntelligenceModel(n_clusters=5, random_state=42)
    clustered_df = model.fit_transform_dataset(df)
    return clustered_df, model


# Load data and pipeline
try:
    df, ml_model = load_and_prepare_data()
except Exception as e:
    st.error(f"Error loading workforce data: {str(e)}")
    st.stop()


# -------------------------------------------------------------
# SIDEBAR NAVIGATION & GLOBAL FILTERS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #1F2937; margin-bottom: 16px;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #0EA5E9; letter-spacing: 0.08em; text-transform: uppercase;">Enterprise Analytics</div>
        <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin-top: 2px;">Palo Alto Networks</div>
        <div style="font-size: 0.78rem; color: #94A3B8;">Career Intelligence & Retention</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.74rem; font-weight: 600; text-transform: uppercase; color: #94A3B8; margin-bottom: 8px;'>Navigation</div>", unsafe_allow_html=True)
    selected_module = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Career Path Clustering",
            "Promotion Gap Monitor",
            "Retention Opportunity Panel",
            "Managerial & Leadership Impact",
            "Career Simulator & What-If Lab",
            "Workforce Data Explorer",
            "Research & Executive Brief"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<div style='padding-top: 14px; border-top: 1px solid #1F2937; margin-top: 14px; font-size: 0.74rem; font-weight: 600; text-transform: uppercase; color: #94A3B8; margin-bottom: 8px;'>Workforce Filters</div>", unsafe_allow_html=True)

    # Filter: Department
    departments = ["All"] + sorted(df['Department'].unique().tolist())
    selected_dept = st.selectbox("Department", departments, index=0)

    # Filter: Role
    available_roles = df['JobRole'].unique().tolist()
    if selected_dept != "All":
        available_roles = df[df['Department'] == selected_dept]['JobRole'].unique().tolist()
    
    selected_roles = st.multiselect("Job Roles", options=sorted(available_roles), default=[])

    # Filter: Attrition Status
    attrition_filter = st.selectbox("Workforce Cohort", ["Active Workforce Only (Recommended)", "All Employees", "Attrited Only"])

    # Filter: Career Stage
    stages = ["All"] + sorted(df['CareerStage'].unique().tolist())
    selected_stage = st.selectbox("Career Stage", stages, index=0)

    # Filter: Career Archetype Clusters (Cluster Explorer)
    available_clusters = sorted(df['CareerCluster'].unique().tolist())
    selected_clusters = st.multiselect("Career Archetypes", options=available_clusters, default=[])

    # Filter: Promotion Risk Slider
    min_risk_threshold = st.slider("Minimum Stagnation Risk Score", 0, 100, 0, step=5)

    st.markdown("""
    <div style="padding-top: 20px; border-top: 1px solid #1F2937; margin-top: 20px; font-size: 0.72rem; color: #64748B; text-align: center;">
        PANW Career Intelligence Engine v1.0<br/>
        Unsupervised Workforce Modeling
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# FILTER APPLICATION
# -------------------------------------------------------------
filtered_df = df.copy()

if selected_dept != "All":
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]

if selected_roles:
    filtered_df = filtered_df[filtered_df['JobRole'].isin(selected_roles)]

if selected_clusters:
    filtered_df = filtered_df[filtered_df['CareerCluster'].isin(selected_clusters)]

if attrition_filter == "Active Workforce Only (Recommended)":
    filtered_df = filtered_df[filtered_df['Attrition'] == 0]
elif attrition_filter == "Attrited Only":
    filtered_df = filtered_df[filtered_df['Attrition'] == 1]

if selected_stage != "All":
    filtered_df = filtered_df[filtered_df['CareerStage'] == selected_stage]

if min_risk_threshold > 0:
    filtered_df = filtered_df[filtered_df['PromotionGapRiskScore'] >= min_risk_threshold]


# -------------------------------------------------------------
# MODULE 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
if selected_module == "Executive Overview":
    render_header(
        title="Executive Overview & Workforce Health",
        subtitle="Enterprise career velocity, stagnation risk distributions, and proactive talent retention indicators.",
        tag="Executive Cockpit"
    )

    kpis = get_executive_kpis(filtered_df)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("Total Headcount", f"{kpis['total_employees']:,}", f"{kpis['active_employees']} Active Staff", "#0EA5E9")
    with c2:
        render_metric_card("Stagnation Risk Rate", f"{kpis['high_promo_risk_pct']}%", f"{kpis['high_promo_risk']} High-Risk Profiles", "#F43F5E")
    with c3:
        render_metric_card("Retention Action Queue", f"{kpis['immediate_roi_interventions']}", f"{kpis['immediate_roi_pct']}% of Active Workforce", "#F59E0B")
    with c4:
        render_metric_card("Mean Promotion Gap", f"{kpis['avg_years_without_promo']} yrs", "Years Since Last Advancement", "#6366F1")
    with c5:
        render_metric_card("Workforce Attrition Rate", f"{kpis['attrition_rate']}%", "Historical Baseline", "#64748B")

    st.markdown("<br/>", unsafe_allow_html=True)

    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Career Archetype Distribution by Stagnation Risk</div>", unsafe_allow_html=True)
        fig_bar = px.histogram(
            filtered_df,
            x='CareerCluster',
            color='PromotionGapRiskLevel',
            barmode='group',
            color_discrete_map={'Low Risk': '#10B981', 'Medium Risk': '#F59E0B', 'High Risk': '#F43F5E'},
            title=""
        )
        fig_bar.update_layout(
            paper_bgcolor='#111827',
            plot_bgcolor='#0B0F17',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            xaxis=dict(gridcolor='#1E293B', title=''),
            yaxis=dict(gridcolor='#1E293B', title='Headcount'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='#111827'),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Department Retention Priority Share</div>", unsafe_allow_html=True)
        dept_risk = filtered_df.groupby('Department')['RetentionOpportunityIndex'].mean().reset_index()
        fig_donut = px.pie(
            dept_risk,
            names='Department',
            values='RetentionOpportunityIndex',
            hole=0.6,
            color='Department',
            color_discrete_sequence=['#0EA5E9', '#6366F1', '#38BDF8'],
            title=""
        )
        fig_donut.update_layout(
            paper_bgcolor='#111827',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(l=20, r=20, t=20, b=30)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    high_urgency_count = len(filtered_df[filtered_df['RetentionPriorityLevel'] == 'Immediate Action'])
    st.markdown(f"""
    <div class="custom-alert">
        <strong>Proactive Intelligence Alert:</strong> Identified <strong>{high_urgency_count} active employees</strong> with high performance ratings who are experiencing substantial promotion gaps. Initiating structured career reviews now directly prevents voluntary disengagement.
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# MODULE 2: CAREER PATH CLUSTERING
# -------------------------------------------------------------
elif selected_module == "Career Path Clustering":
    render_header(
        title="Career Path Clustering & Archetype Segmentation",
        subtitle="Unsupervised multi-dimensional segmentation (K-Means & Hierarchical) uncovering career trajectory archetypes.",
        tag="Unsupervised ML"
    )

    tab_2d, tab_3d, tab_radar, tab_benchmarks = st.tabs([
        "2D PCA Cluster Map",
        "3D Spatial Projection",
        "Archetype Radar Profiles",
        "Model Validation & Metrics"
    ])

    with tab_2d:
        st.plotly_chart(create_pca_scatter_plot(filtered_df, is_3d=False), use_container_width=True)
        st.caption("PCA reduces 12 career progression dimensions to 2 orthogonal axes capturing the majority of trajectory variance.")

    with tab_3d:
        st.plotly_chart(create_pca_scatter_plot(filtered_df, is_3d=True), use_container_width=True)
        st.caption("3D interactive projection enabling spatial inspection and rotation across career cluster boundaries.")

    with tab_radar:
        col_r_left, col_r_right = st.columns([6, 4])
        with col_r_left:
            radar_dict = get_archetype_radar_data(filtered_df)
            st.plotly_chart(create_radar_chart(radar_dict), use_container_width=True)
        with col_r_right:
            st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 12px;'>Archetype Definitions & Prescriptive Strategies</div>", unsafe_allow_html=True)
            for arch_name, arch_info in ARCHETYPE_DESCRIPTIONS.items():
                st.markdown(f"""
                <div style="background: #111827; border: 1px solid #1F2937; border-left: 3px solid {arch_info['color']}; padding: 12px 14px; border-radius: 6px; margin-bottom: 10px;">
                    <div style="font-size: 0.86rem; font-weight: 600; color: {arch_info['color']};">{arch_info['badge']}</div>
                    <div style="font-size: 0.80rem; color: #CBD5E1; margin: 4px 0 2px 0;">{arch_info['summary']}</div>
                    <div style="font-size: 0.76rem; color: #94A3B8;"><strong>Talent Strategy:</strong> {arch_info['strategy']}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab_benchmarks:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 12px;'>Unsupervised Cluster Quality Metrics</div>", unsafe_allow_html=True)
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            render_metric_card("K-Means Silhouette", f"{ml_model.metrics.get('silhouette_kmeans', 0.22):.3f}", "Optimal Partitioning Index", "#0EA5E9")
        with m_col2:
            render_metric_card("Hierarchical Silhouette", f"{ml_model.metrics.get('silhouette_hierarchical', 0.21):.3f}", "Agglomerative Baseline", "#6366F1")
        with m_col3:
            render_metric_card("Calinski-Harabasz", f"{ml_model.metrics.get('calinski_harabasz', 341.0):.1f}", "Variance Ratio Criterion", "#10B981")
        with m_col4:
            render_metric_card("Cumulative PCA Variance", f"{ml_model.metrics.get('pca_3d_variance', 0.63)*100:.1f}%", "Captured Information Ratio", "#8B5CF6")

        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin: 16px 0 8px 0;'>Cluster Centroid Means Across Feature Dimensions</div>", unsafe_allow_html=True)
        cluster_summary = filtered_df.groupby('CareerCluster')[CLUSTERING_FEATURES + ['PromotionGapRiskScore']].mean().round(2)
        st.dataframe(cluster_summary, use_container_width=True)


# -------------------------------------------------------------
# MODULE 3: PROMOTION GAP MONITOR
# -------------------------------------------------------------
elif selected_module == "Promotion Gap Monitor":
    render_header(
        title="Promotion Gap & Career Stagnation Monitor",
        subtitle="Role-level velocity tracking, stagnation heatmaps, and threshold-based bottleneck detection.",
        tag="Stagnation Analytics"
    )

    col_gap_1, col_gap_2 = st.columns([6, 4])

    with col_gap_1:
        st.plotly_chart(create_stagnation_heatmap(filtered_df), use_container_width=True)

    with col_gap_2:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Role Tenure vs Promotion Latency</div>", unsafe_allow_html=True)
        fig_scatter = px.scatter(
            filtered_df,
            x='YearsInCurrentRole',
            y='YearsSinceLastPromotion',
            color='PromotionGapRiskLevel',
            size='PromotionGapRiskScore',
            color_discrete_map={'Low Risk': '#10B981', 'Medium Risk': '#F59E0B', 'High Risk': '#F43F5E'},
            hover_name='EmployeeID',
            hover_data=['JobRole', 'Department', 'YearsAtCompany'],
            title=""
        )
        fig_scatter.update_layout(
            paper_bgcolor='#111827',
            plot_bgcolor='#0B0F17',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            xaxis=dict(gridcolor='#1E293B', title='Years in Current Role'),
            yaxis=dict(gridcolor='#1E293B', title='Years Since Last Promotion'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='#111827'),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin: 16px 0 8px 0;'>Department & Job Role Stagnation Breakdown</div>", unsafe_allow_html=True)
    stagnation_matrix = get_role_stagnation_matrix(filtered_df)
    st.dataframe(stagnation_matrix, use_container_width=True, hide_index=True)


# -------------------------------------------------------------
# MODULE 4: RETENTION OPPORTUNITY PANEL
# -------------------------------------------------------------
elif selected_module == "Retention Opportunity Panel":
    render_header(
        title="Proactive Retention Opportunity Action Panel",
        subtitle="Prioritized roster of active high-performing talent with career stagnation signals and prescriptive interventions.",
        tag="Prescriptive AI"
    )

    action_filter = st.selectbox(
        "Filter by Prescriptive Action Type:",
        ["All Actions", "Fast-Track Promotion Review", "Lateral Role Rotation", "Executive Upskilling", "Mentorship Realignment"]
    )

    priority_queue = get_retention_priority_queue(filtered_df, top_n=200)

    if action_filter != "All Actions":
        priority_queue = priority_queue[priority_queue['PrescriptiveAction'].str.contains(action_filter, case=False, na=False)]

    col_q1, col_q2 = st.columns([7, 3])

    with col_q1:
        st.markdown(f"<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>High-Priority Action Candidates ({len(priority_queue)} Total)</div>", unsafe_allow_html=True)
        st.dataframe(
            priority_queue,
            use_container_width=True,
            hide_index=True,
            column_config={
                "RetentionOpportunityIndex": st.column_config.ProgressColumn("Retention Opportunity Index", min_value=0, max_value=100, format="%.1f"),
                "PromotionGapRiskScore": st.column_config.ProgressColumn("Promotion Risk Score", min_value=0, max_value=100, format="%.1f")
            }
        )

    with col_q2:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Prescriptive Action Breakdown</div>", unsafe_allow_html=True)
        action_counts = priority_queue['PrescriptiveAction'].value_counts().reset_index()
        action_counts.columns = ['PrescriptiveAction', 'Count']
        
        # Clean compact labels for donut chart
        label_map = {
            "Fast-Track Promotion Review & Compensation Adjustment": "Promotion Review",
            "Lateral Role Rotation & Cross-Department Project Assignment": "Role Rotation",
            "Executive Upskilling & Leadership Accelerator Program": "Executive Upskilling",
            "Mentorship Realignment & Skip-Level Career Planning": "Mentorship Realignment",
            "Standard Annual Career Progression Tracking": "Standard Tracking",
            "Exit Analysis & Knowledge Transfer": "Exit Analysis"
        }
        action_counts['ShortAction'] = action_counts['PrescriptiveAction'].map(lambda x: label_map.get(x, x))
        
        fig_actions = px.pie(
            action_counts,
            names='ShortAction',
            values='Count',
            hole=0.55,
            color_discrete_sequence=['#0EA5E9', '#6366F1', '#F59E0B', '#F43F5E', '#10B981'],
            title=""
        )
        fig_actions.update_layout(
            paper_bgcolor='#111827',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(l=10, r=10, t=10, b=20)
        )
        st.plotly_chart(fig_actions, use_container_width=True)

    csv_data = priority_queue.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Retention Action Roster (CSV)",
        data=csv_data,
        file_name="panw_retention_opportunity_roster.csv",
        mime="text/csv"
    )


# -------------------------------------------------------------
# MODULE 5: MANAGERIAL IMPACT
# -------------------------------------------------------------
elif selected_module == "Managerial & Leadership Impact":
    render_header(
        title="Managerial Continuity & Leadership Impact Matrix",
        subtitle="Evaluating the correlation between supervisor tenure, team career progression, and stagnation dyads.",
        tag="Leadership Analytics"
    )

    mgr_matrix = get_manager_insight_matrix(filtered_df)
    st.plotly_chart(create_manager_impact_chart(mgr_matrix), use_container_width=True)

    col_m1, col_m2 = st.columns([5, 5])

    with col_m1:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Manager Tenure Cohort Statistics</div>", unsafe_allow_html=True)
        st.dataframe(mgr_matrix, use_container_width=True, hide_index=True)

    with col_m2:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Manager Stability Impact Distribution</div>", unsafe_allow_html=True)
        impact_counts = filtered_df['ManagerStabilityImpact'].value_counts().reset_index()
        impact_counts.columns = ['StabilityCategory', 'Headcount']
        fig_mgr_pie = px.pie(
            impact_counts,
            names='StabilityCategory',
            values='Headcount',
            color='StabilityCategory',
            color_discrete_map={
                'Prolonged Stagnant Manager Dyad': '#F43F5E',
                'Stable Leadership Continuity': '#10B981',
                'Moderate Manager Continuity': '#6366F1',
                'Recent Manager Transition': '#F59E0B'
            },
            hole=0.55
        )
        fig_mgr_pie.update_layout(
            paper_bgcolor='#111827',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(l=20, r=20, t=20, b=30)
        )
        st.plotly_chart(fig_mgr_pie, use_container_width=True)

    st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin: 18px 0 8px 0;'>Team-Level Stagnation & Leadership Bottleneck Signals</div>", unsafe_allow_html=True)
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


# -------------------------------------------------------------
# MODULE 6: CAREER SIMULATOR & WHAT-IF LAB
# -------------------------------------------------------------
elif selected_module == "Career Simulator & What-If Lab":
    render_header(
        title="Individual Career Simulator & What-If Lab",
        subtitle="Simulate talent management interventions (promotions, lateral rotations, upskilling) and observe real-time risk mitigation.",
        tag="Simulation Engine"
    )

    sim_col1, sim_col2 = st.columns([4, 6])

    with sim_col1:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Target Employee Profile</div>", unsafe_allow_html=True)
        sample_emp_ids = filtered_df['EmployeeID'].tolist()
        selected_emp_id = st.selectbox("Select Employee ID", sample_emp_ids, index=0 if sample_emp_ids else None)

        if selected_emp_id:
            emp_row = df[df['EmployeeID'] == selected_emp_id].iloc[0]
            st.markdown(f"""
            <div style="background: #111827; border: 1px solid #1F2937; border-radius: 6px; padding: 12px 14px; margin-bottom: 12px;">
                <div style="font-size: 0.92rem; font-weight: 700; color: #F8FAFC;">{emp_row['EmployeeID']} &mdash; {emp_row['JobRole']}</div>
                <div style="font-size: 0.80rem; color: #94A3B8; margin-top: 4px;">Department: {emp_row['Department']} | Job Level: {emp_row['JobLevel']}</div>
                <div style="font-size: 0.80rem; color: #94A3B8;">Years at Company: {emp_row['YearsAtCompany']} | Years in Current Role: {emp_row['YearsInCurrentRole']}</div>
                <div style="font-size: 0.80rem; color: #94A3B8;">Years Since Last Promotion: {emp_row['YearsSinceLastPromotion']} | Performance: {emp_row['PerformanceRating']}/4</div>
                <div style="font-size: 0.80rem; color: #0EA5E9; margin-top: 4px; font-weight: 600;">Current Cluster: {emp_row['CareerCluster']}</div>
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

        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin: 12px 0 6px 0;'>Intervention Levers</div>", unsafe_allow_html=True)
        sim_action = st.radio(
            "Talent Action Preset:",
            ["Manual Customization", "Award Promotion", "Assign Lateral Role Rotation", "Enroll in Executive Training"]
        )

        if sim_action == "Award Promotion":
            sim_promo_years = 0
            sim_role_years = 0
            sim_job_level = min(int(baseline_dict.get('JobLevel', 1)) + 1, 5)
            sim_trainings = int(baseline_dict.get('TrainingTimesLastYear', 2)) + 1
            sim_salary_hike = int(baseline_dict.get('PercentSalaryHike', 15)) + 8
        elif sim_action == "Assign Lateral Role Rotation":
            sim_promo_years = int(baseline_dict.get('YearsSinceLastPromotion', 2))
            sim_role_years = 0
            sim_job_level = int(baseline_dict.get('JobLevel', 1))
            sim_trainings = int(baseline_dict.get('TrainingTimesLastYear', 2)) + 2
            sim_salary_hike = int(baseline_dict.get('PercentSalaryHike', 15))
        elif sim_action == "Enroll in Executive Training":
            sim_promo_years = int(baseline_dict.get('YearsSinceLastPromotion', 2))
            sim_role_years = int(baseline_dict.get('YearsInCurrentRole', 2))
            sim_job_level = int(baseline_dict.get('JobLevel', 1))
            sim_trainings = 5
            sim_salary_hike = int(baseline_dict.get('PercentSalaryHike', 15))
        else:
            sim_promo_years = st.slider("Years Since Last Promotion", 0, 15, int(baseline_dict.get('YearsSinceLastPromotion', 2)))
            sim_role_years = st.slider("Years in Current Role", 0, 15, int(baseline_dict.get('YearsInCurrentRole', 2)))
            sim_trainings = st.slider("Training Programs Attended", 0, 6, int(baseline_dict.get('TrainingTimesLastYear', 2)))
            sim_job_level = st.slider("Job Level", 1, 5, int(baseline_dict.get('JobLevel', 1)))
            sim_salary_hike = st.slider("Percent Salary Hike (%)", 0, 35, int(baseline_dict.get('PercentSalaryHike', 15)))

    with sim_col2:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;'>Simulation Outcome & Trajectory Shift</div>", unsafe_allow_html=True)
        
        simulated_payload = {
            **baseline_dict,
            'YearsSinceLastPromotion': sim_promo_years,
            'YearsInCurrentRole': sim_role_years,
            'TrainingTimesLastYear': sim_trainings,
            'JobLevel': sim_job_level,
            'PercentSalaryHike': sim_salary_hike
        }

        # Predict with ML pipeline
        pred_res = ml_model.predict_single(simulated_payload)

        orig_risk = float(baseline_dict.get('PromotionGapRiskScore', 50.0))
        new_risk = float(pred_res['PromotionGapRiskScore'])
        risk_diff = new_risk - orig_risk

        orig_roi = float(baseline_dict.get('RetentionOpportunityIndex', 60.0))
        new_roi = float(pred_res['RetentionOpportunityIndex'])

        r1, r2, r3 = st.columns(3)
        with r1:
            render_metric_card(
                "Stagnation Risk Score",
                f"{new_risk:.1f}",
                f"{risk_diff:+.1f} Shift from Baseline",
                "#10B981" if new_risk < 35 else "#F43F5E"
            )
        with r2:
            render_metric_card(
                "Predicted Archetype",
                pred_res['CareerCluster'],
                "Trajectory Classification",
                "#0EA5E9"
            )
        with r3:
            render_metric_card(
                "Retention Priority",
                f"{new_roi:.1f}",
                "Workforce Index",
                "#F59E0B"
            )

        st.markdown("<div style='font-size: 0.95rem; font-weight: 600; color: #F8FAFC; margin: 16px 0 8px 0;'>Simulated State Relative to Enterprise Career Space</div>", unsafe_allow_html=True)
        fig_sim = px.scatter(
            df,
            x='PCA1',
            y='PCA2',
            color='CareerCluster',
            color_discrete_map={k: COLOR_PALETTE.get(k, '#94A3B8') for k in df['CareerCluster'].unique()},
            opacity=0.35,
            title=""
        )
        
        # Add simulated point
        fig_sim.add_trace(go.Scatter(
            x=[pred_res['PCA1']],
            y=[pred_res['PCA2']],
            mode='markers+text',
            name='Simulated State',
            text=['Simulated Position'],
            textposition='top center',
            marker=dict(size=14, color='#38BDF8', symbol='diamond', line=dict(width=2, color='#FFFFFF'))
        ))

        fig_sim.update_layout(
            paper_bgcolor='#111827',
            plot_bgcolor='#0B0F17',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(l=20, r=20, t=20, b=30)
        )
        st.plotly_chart(fig_sim, use_container_width=True)


# -------------------------------------------------------------
# MODULE 7: WORKFORCE DATA EXPLORER
# -------------------------------------------------------------
elif selected_module == "Workforce Data Explorer":
    render_header(
        title="Workforce Data Explorer & Export Center",
        subtitle="Search, filter, inspect derived KPI attributes, and export custom enterprise subsets.",
        tag="Data Center"
    )

    search_query = st.text_input("Search records by Employee ID, Department, or Role:", "")

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
        label="Export Filtered Workforce Dataset (CSV)",
        data=csv_export,
        file_name="panw_career_intelligence_filtered.csv",
        mime="text/csv"
    )


# -------------------------------------------------------------
# MODULE 8: RESEARCH & EXECUTIVE BRIEF
# -------------------------------------------------------------
elif selected_module == "Research & Executive Brief":
    render_header(
        title="Research Documentation & Executive Policy Briefing",
        subtitle="Formal academic research methodology, mathematical derivations, and C-suite/government policy recommendations.",
        tag="Documentation"
    )

    doc_tab1, doc_tab2 = st.tabs(["Research Paper (Full Text)", "Executive Summary & Policy Brief"])

    with doc_tab1:
        research_paper_path = os.path.join(os.path.dirname(__file__), "RESEARCH_PAPER.md")
        if os.path.exists(research_paper_path):
            with open(research_paper_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())
        else:
            st.info("Research paper document is available in the repository root as RESEARCH_PAPER.md.")

    with doc_tab2:
        exec_summary_path = os.path.join(os.path.dirname(__file__), "EXECUTIVE_SUMMARY.md")
        if os.path.exists(exec_summary_path):
            with open(exec_summary_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())
        else:
            st.info("Executive summary document is available in the repository root as EXECUTIVE_SUMMARY.md.")
