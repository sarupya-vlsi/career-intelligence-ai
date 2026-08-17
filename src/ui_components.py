"""
UI Styling & Visualization Components
Enterprise Dark Design System with Polished Plotly Visualizations (No Emojis)
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Any


COLOR_PALETTE = {
    'Fast-Track Performers': '#0EA5E9',       # Sky Cyan
    'Stable Long-Term Contributors': '#6366F1', # Indigo
    'Early-Career Explorers': '#10B981',       # Emerald
    'Promotion-Stalled Employees': '#F59E0B',  # Amber
    'High-Risk Stagnation Profiles': '#F43F5E',# Rose
    'Primary': '#0EA5E9',
    'Secondary': '#6366F1',
    'Background': '#0B0F17',
    'CardBg': '#111827',
    'Border': '#1F2937',
    'TextPrimary': '#F9FAFB',
    'TextMuted': '#9CA3AF'
}

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #E2E8F0;
    -webkit-font-smoothing: antialiased;
}

/* Background */
.stApp {
    background-color: #0B0F17;
    background-image: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.04) 0px, transparent 50%),
                      radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.04) 0px, transparent 50%);
}

/* Top Navigation Bar / Brand Header */
.brand-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 24px;
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 8px;
    margin-bottom: 24px;
}

.brand-title {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #F8FAFC;
    margin: 0;
}

.brand-subtitle {
    font-size: 0.82rem;
    color: #94A3B8;
    margin-top: 3px;
    margin-bottom: 0;
}

.brand-tag {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #0EA5E9;
    background: rgba(14, 165, 233, 0.1);
    border: 1px solid rgba(14, 165, 233, 0.25);
    padding: 4px 10px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
}

/* Page Header */
.page-header {
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1F2937;
}

.page-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.015em;
    margin: 0 0 4px 0;
}

.page-description {
    font-size: 0.86rem;
    color: #94A3B8;
    line-height: 1.4;
    margin: 0;
}

/* Enterprise Metric Cards */
div[data-testid="stColumn"] > div {
    height: 100%;
}

.enterprise-card {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 8px;
    padding: 14px 16px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    height: 135px !important;
    max-height: 135px !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-sizing: border-box;
    overflow: hidden;
}

.enterprise-card:hover {
    border-color: #374151;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94A3B8;
    margin-bottom: 4px;
}

.metric-val {
    color: #F8FAFC;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
    word-break: break-word;
}

.metric-meta {
    font-size: 0.74rem;
    font-weight: 500;
    color: #64748B;
    margin-top: auto;
}

/* Clean Chips & Status Tags */
.chip {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.chip-blue {
    background: rgba(14, 165, 233, 0.12);
    color: #38BDF8;
    border: 1px solid rgba(14, 165, 233, 0.25);
}

.chip-amber {
    background: rgba(245, 158, 11, 0.12);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.25);
}

.chip-red {
    background: rgba(244, 63, 94, 0.12);
    color: #FB7185;
    border: 1px solid rgba(244, 63, 94, 0.25);
}

.chip-emerald {
    background: rgba(16, 185, 129, 0.12);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.25);
}

/* Sidebar Clean Styling */
section[data-testid="stSidebar"] {
    background-color: #0C1019 !important;
    border-right: 1px solid #1F2937 !important;
}

/* Tab Headers */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background-color: #111827;
    padding: 4px;
    border-radius: 6px;
    border: 1px solid #1F2937;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 5px;
    color: #94A3B8;
    font-weight: 500;
    font-size: 0.85rem;
    padding: 6px 14px;
}

.stTabs [aria-selected="true"] {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    font-weight: 600 !important;
    border: 1px solid #334155 !important;
}

/* Dataframe Clean Styling */
div[data-testid="stDataFrame"] {
    border: 1px solid #1F2937;
    border-radius: 6px;
    overflow: hidden;
}

/* Custom Alert Banner */
.custom-alert {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid #1E293B;
    border-left: 3px solid #0EA5E9;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 0.85rem;
    color: #CBD5E1;
    line-height: 1.45;
    margin: 14px 0;
}
</style>
"""


def apply_custom_css():
    """Injects custom enterprise CSS styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, tag: str = "Enterprise ML"):
    """Renders clean corporate page header."""
    st.markdown(f"""
    <div class="page-header">
        <div style="display: flex; align-items: flex-start; justify-content: space-between;">
            <div>
                <h1 class="page-title">{title}</h1>
                <p class="page-description">{subtitle}</p>
            </div>
            <span class="brand-tag">{tag}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, meta: str = "", accent_color: str = "#0EA5E9"):
    """Renders crisp enterprise KPI card with guaranteed equal height and adaptive typography."""
    val_str = str(value)
    if len(val_str) > 22:
        val_style = "font-size: 0.88rem; line-height: 1.25; font-weight: 600;"
    elif len(val_str) > 14:
        val_style = "font-size: 0.98rem; line-height: 1.2; font-weight: 700;"
    elif len(val_str) > 8:
        val_style = "font-size: 1.25rem; line-height: 1.15; font-weight: 700;"
    else:
        val_style = "font-size: 1.55rem; line-height: 1.1; font-weight: 700;"

    st.markdown(f"""
    <div class="enterprise-card" style="border-top: 2px solid {accent_color};">
        <div>
            <div class="metric-label">{title}</div>
            <div class="metric-val" style="{val_style}">{value}</div>
        </div>
        <div class="metric-meta" style="color: {accent_color};">{meta}</div>
    </div>
    """, unsafe_allow_html=True)


def create_pca_scatter_plot(df: pd.DataFrame, is_3d: bool = False) -> go.Figure:
    """Creates clean Plotly PCA cluster visualization."""
    color_map = {k: COLOR_PALETTE.get(k, '#94A3B8') for k in df['CareerCluster'].unique()}
    
    if is_3d:
        fig = px.scatter_3d(
            df,
            x='PCA1',
            y='PCA2',
            z='PCA3',
            color='CareerCluster',
            color_discrete_map=color_map,
            hover_name='EmployeeID',
            hover_data={
                'JobRole': True,
                'Department': True,
                'YearsAtCompany': True,
                'YearsSinceLastPromotion': True,
                'PromotionGapRiskScore': True,
                'PCA1': False,
                'PCA2': False,
                'PCA3': False
            },
            title="3D Principal Component Projection of Career Space"
        )
        fig.update_layout(
            scene=dict(
                xaxis=dict(backgroundcolor="#0B0F17", gridcolor="#1E293B", showbackground=True),
                yaxis=dict(backgroundcolor="#0B0F17", gridcolor="#1E293B", showbackground=True),
                zaxis=dict(backgroundcolor="#0B0F17", gridcolor="#1E293B", showbackground=True),
            ),
            margin=dict(l=0, r=0, b=0, t=10)
        )
    else:
        fig = px.scatter(
            df,
            x='PCA1',
            y='PCA2',
            color='CareerCluster',
            color_discrete_map=color_map,
            hover_name='EmployeeID',
            hover_data={
                'JobRole': True,
                'Department': True,
                'YearsAtCompany': True,
                'YearsInCurrentRole': True,
                'YearsSinceLastPromotion': True,
                'PromotionGapRiskScore': True,
                'RetentionOpportunityIndex': True,
                'PCA1': False,
                'PCA2': False
            },
            title=""
        )
        fig.update_traces(marker=dict(size=7, opacity=0.85, line=dict(width=0.5, color='#0B0F17')))

    fig.update_layout(
        paper_bgcolor='#111827',
        plot_bgcolor='#0B0F17',
        font=dict(color='#E2E8F0', family='Inter', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(17, 24, 39, 0.9)',
            bordercolor='#1F2937',
            borderwidth=1,
            font=dict(size=11)
        ),
        xaxis=dict(gridcolor='#1E293B', zerolinecolor='#334155'),
        yaxis=dict(gridcolor='#1E293B', zerolinecolor='#334155'),
        margin=dict(l=20, r=20, t=10, b=45)
    )
    return fig


def create_radar_chart(radar_dict: Dict[str, List[float]]) -> go.Figure:
    """Creates multi-archetype radar comparison chart."""
    categories = [
        'Career Velocity', 'Promotion Recency', 'Training Agility',
        'Organizational Tenure', 'Comp Ratio', 'Job Satisfaction'
    ]
    
    fig = go.Figure()
    
    for arch, values in radar_dict.items():
        color = COLOR_PALETTE.get(arch, '#0EA5E9')
        r_vals = values + [values[0]]
        cat_vals = categories + [categories[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=r_vals,
            theta=cat_vals,
            fill='toself',
            name=arch,
            line=dict(color=color, width=1.8),
            opacity=0.45
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                color='#64748B',
                gridcolor='#1E293B',
                linecolor='#1E293B'
            ),
            angularaxis=dict(
                color='#94A3B8',
                gridcolor='#1E293B',
                linecolor='#1E293B'
            ),
            bgcolor='#0B0F17'
        ),
        paper_bgcolor='#111827',
        font=dict(color='#E2E8F0', family='Inter', size=11),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            bgcolor='#111827',
            font=dict(size=10)
        ),
        margin=dict(l=35, r=35, b=50, t=20)
    )
    return fig


def create_stagnation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Generates clean department vs job role stagnation heatmap."""
    pivot = df.pivot_table(
        index='JobRole',
        columns='Department',
        values='PromotionGapRiskScore',
        aggfunc='mean'
    ).fillna(0).round(1)

    fig = px.imshow(
        pivot,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='Blues',
        title="Mean Promotion Stagnation Risk Score by Department & Role"
    )
    fig.update_layout(
        paper_bgcolor='#111827',
        plot_bgcolor='#0B0F17',
        font=dict(color='#E2E8F0', family='Inter', size=11),
        title_font=dict(size=13, color='#F8FAFC', family='Inter'),
        coloraxis_colorbar=dict(
            title=dict(text="Risk (0-100)", font=dict(size=11, color='#94A3B8')),
            tickfont=dict(size=10, color='#94A3B8')
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def create_manager_impact_chart(mgr_df: pd.DataFrame) -> go.Figure:
    """Creates clean manager tenure vs promotion gap and stagnation chart."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=mgr_df['ManagerTenureBin'].astype(str),
        y=mgr_df['AvgPromoRiskScore'],
        name='Avg Promotion Risk Score',
        marker_color='#3B82F6',
        opacity=0.85
    ))

    fig.add_trace(go.Scatter(
        x=mgr_df['ManagerTenureBin'].astype(str),
        y=mgr_df['AvgYearsSincePromo'],
        name='Avg Years Without Promotion',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#0EA5E9', width=2.5),
        marker=dict(size=7, color='#0EA5E9')
    ))

    fig.update_layout(
        title="Manager Continuity vs Promotion Latency and Risk",
        paper_bgcolor='#111827',
        plot_bgcolor='#0B0F17',
        font=dict(color='#E2E8F0', family='Inter', size=11),
        title_font=dict(size=13, color='#F8FAFC', family='Inter'),
        xaxis=dict(gridcolor='#1E293B'),
        yaxis=dict(
            title=dict(text="Promotion Risk Score", font=dict(size=11, color='#94A3B8')),
            gridcolor='#1E293B'
        ),
        yaxis2=dict(
            title=dict(text="Years Without Promotion", font=dict(size=11, color='#0EA5E9')),
            overlaying='y',
            side='right',
            gridcolor='rgba(0,0,0,0)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='#111827',
            font=dict(size=11)
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
