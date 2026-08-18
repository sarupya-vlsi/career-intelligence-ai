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
    'Fast-Track Performers': '#38BDF8',       # Sky
    'Stable Long-Term Contributors': '#818CF8', # Indigo
    'Early-Career Explorers': '#34D399',       # Emerald
    'Promotion-Stalled Employees': '#FBBF24',  # Amber
    'High-Risk Stagnation Profiles': '#FB7185',# Rose
    'Primary': '#38BDF8',
    'Secondary': '#818CF8',
    'Background': '#090D16',
    'CardBg': '#111726',
    'Border': 'rgba(255, 255, 255, 0.08)',
    'TextPrimary': '#F8FAFC',
    'TextMuted': '#94A3B8'
}

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #E2E8F0;
    -webkit-font-smoothing: antialiased;
}

/* Main background with subtle ambient lighting */
.stApp {
    background-color: #090D16;
    background-image: 
        radial-gradient(circle at 15% 10%, rgba(56, 189, 248, 0.04) 0%, transparent 40%),
        radial-gradient(circle at 85% 90%, rgba(129, 140, 248, 0.04) 0%, transparent 40%);
}

/* Page Header */
.page-header {
    margin-bottom: 22px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.page-title {
    font-size: 1.32rem;
    font-weight: 600;
    color: #F8FAFC;
    letter-spacing: -0.02em;
    margin: 0 0 4px 0;
}

.page-description {
    font-size: 0.84rem;
    color: #94A3B8;
    line-height: 1.45;
    margin: 0;
}

.brand-tag {
    font-size: 0.70rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.2);
    padding: 3px 10px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

/* Metric Cards */
div[data-testid="stColumn"] > div {
    height: 100%;
}

.enterprise-card {
    background: #111726;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
    padding: 16px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    height: 130px !important;
    max-height: 130px !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-sizing: border-box;
    position: relative;
    overflow: hidden;
}

.enterprise-card:hover {
    border-color: rgba(255, 255, 255, 0.14);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
    transform: translateY(-1px);
}

.metric-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    color: #94A3B8;
    margin-bottom: 4px;
}

.metric-val {
    color: #F8FAFC;
    letter-spacing: -0.03em;
    margin-bottom: 2px;
    word-break: break-word;
}

.metric-meta {
    font-size: 0.73rem;
    font-weight: 500;
    margin-top: auto;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0B0F19 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.84rem;
    font-weight: 500;
    color: #94A3B8;
    padding: 4px 6px;
    border-radius: 6px;
    transition: background 0.15s ease, color 0.15s ease;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    color: #F8FAFC;
    background: rgba(255, 255, 255, 0.04);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: #111726;
    padding: 4px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.07);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    color: #94A3B8;
    font-weight: 500;
    font-size: 0.82rem;
    padding: 6px 14px;
}

.stTabs [aria-selected="true"] {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Dataframe Clean Styling */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
    overflow: hidden;
}

/* Content Card Container */
.content-box {
    background: #111726;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 14px;
}

/* Custom Alert Banner */
.custom-alert {
    background: rgba(17, 23, 38, 0.9);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-left: 3px solid #38BDF8;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.83rem;
    color: #CBD5E1;
    line-height: 1.5;
    margin: 14px 0;
}
</style>
"""


def apply_custom_css():
    """Injects custom enterprise CSS styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, tag: str = "Analytics"):
    """Renders clean corporate page header."""
    st.markdown(f"""
    <div class="page-header">
        <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 16px;">
            <div>
                <h1 class="page-title">{title}</h1>
                <p class="page-description">{subtitle}</p>
            </div>
            <span class="brand-tag">{tag}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, meta: str = "", accent_color: str = "#38BDF8"):
    """Renders crisp modern KPI card with adaptive typography and clean indicator."""
    val_str = str(value)
    if len(val_str) > 22:
        val_style = "font-size: 0.88rem; line-height: 1.25; font-weight: 600;"
    elif len(val_str) > 14:
        val_style = "font-size: 0.98rem; line-height: 1.2; font-weight: 600;"
    elif len(val_str) > 8:
        val_style = "font-size: 1.20rem; line-height: 1.15; font-weight: 600;"
    else:
        val_style = "font-size: 1.48rem; line-height: 1.1; font-weight: 600;"

    st.markdown(f"""
    <div class="enterprise-card" style="box-shadow: inset 0 2px 0 {accent_color};">
        <div>
            <div class="metric-label">{title}</div>
            <div class="metric-val" style="{val_style}">{value}</div>
        </div>
        <div class="metric-meta" style="color: {accent_color};">
            <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:{accent_color};"></span>
            {meta}
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_pca_scatter_plot(df: pd.DataFrame, is_3d: bool = False) -> go.Figure:
    """Creates clean Plotly PCA cluster visualization with modern aesthetic."""
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
            title=""
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            scene=dict(
                xaxis=dict(backgroundcolor="#0B0F19", gridcolor="rgba(255,255,255,0.06)", showbackground=True),
                yaxis=dict(backgroundcolor="#0B0F19", gridcolor="rgba(255,255,255,0.06)", showbackground=True),
                zaxis=dict(backgroundcolor="#0B0F19", gridcolor="rgba(255,255,255,0.06)", showbackground=True),
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
        fig.update_traces(marker=dict(size=7, opacity=0.85, line=dict(width=0.5, color='#090D16')))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0', family='Inter', size=11),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(17, 23, 38, 0.8)',
                bordercolor='rgba(255, 255, 255, 0.08)',
                borderwidth=1,
                font=dict(size=11)
            ),
            xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
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
        color = COLOR_PALETTE.get(arch, '#38BDF8')
        r_vals = values + [values[0]]
        cat_vals = categories + [categories[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=r_vals,
            theta=cat_vals,
            fill='toself',
            name=arch,
            line=dict(color=color, width=1.6),
            opacity=0.35
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                color='#64748B',
                gridcolor='rgba(255,255,255,0.06)',
                linecolor='rgba(255,255,255,0.06)'
            ),
            angularaxis=dict(
                color='#94A3B8',
                gridcolor='rgba(255,255,255,0.06)',
                linecolor='rgba(255,255,255,0.06)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0', family='Inter', size=11),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(17, 23, 38, 0.8)',
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
        color_continuous_scale=[[0, '#0F172A'], [0.5, '#1E3A8A'], [1.0, '#38BDF8']],
        title=""
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0', family='Inter', size=11),
        coloraxis_colorbar=dict(
            title=dict(text="Risk Score", font=dict(size=11, color='#94A3B8')),
            tickfont=dict(size=10, color='#94A3B8')
        ),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig


def create_manager_impact_chart(mgr_df: pd.DataFrame) -> go.Figure:
    """Creates clean manager tenure vs promotion gap and stagnation chart."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=mgr_df['ManagerTenureBin'].astype(str),
        y=mgr_df['AvgPromoRiskScore'],
        name='Avg Risk Score',
        marker_color='#6366F1',
        opacity=0.85
    ))

    fig.add_trace(go.Scatter(
        x=mgr_df['ManagerTenureBin'].astype(str),
        y=mgr_df['AvgYearsSincePromo'],
        name='Years Since Promotion',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#38BDF8', width=2),
        marker=dict(size=6, color='#38BDF8')
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0', family='Inter', size=11),
        xaxis=dict(gridcolor='rgba(255,255,255,0.06)'),
        yaxis=dict(
            title=dict(text="Promotion Risk Score", font=dict(size=11, color='#94A3B8')),
            gridcolor='rgba(255,255,255,0.06)'
        ),
        yaxis2=dict(
            title=dict(text="Years Without Promotion", font=dict(size=11, color='#38BDF8')),
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
            bgcolor='rgba(17, 23, 38, 0.8)',
            font=dict(size=11)
        ),
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig

