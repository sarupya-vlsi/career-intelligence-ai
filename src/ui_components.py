"""
UI Styling & Visualization Components
Clean design system with standard 2D Plotly visualizations.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Any


COLOR_PALETTE = {
    'Fast-Track Performers': '#38BDF8',
    'Stable Long-Term Contributors': '#818CF8',
    'Early-Career Explorers': '#34D399',
    'Promotion-Stalled Employees': '#FBBF24',
    'High-Risk Stagnation Profiles': '#FB7185',
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
}

.stApp {
    background-color: #090D16;
}

.page-header {
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.page-title {
    font-size: 1.30rem;
    font-weight: 600;
    color: #F8FAFC;
    margin: 0 0 4px 0;
}

.page-description {
    font-size: 0.84rem;
    color: #94A3B8;
    margin: 0;
}

.brand-tag {
    font-size: 0.72rem;
    font-weight: 500;
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.25);
    padding: 3px 10px;
    border-radius: 9999px;
}

.enterprise-card {
    background: #111726;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 14px 16px;
    height: 120px !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.metric-label {
    font-size: 0.74rem;
    font-weight: 500;
    color: #94A3B8;
    margin-bottom: 4px;
}

.metric-val {
    color: #F8FAFC;
    font-weight: 600;
}

.metric-meta {
    font-size: 0.72rem;
    color: #94A3B8;
}

.custom-alert {
    background: #111726;
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-left: 3px solid #38BDF8;
    border-radius: 6px;
    padding: 12px 14px;
    font-size: 0.82rem;
    color: #CBD5E1;
    margin: 12px 0;
}
</style>
"""


def apply_custom_css():
    """Injects custom CSS styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, tag: str = "Analytics"):
    """Renders page header."""
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
    """Renders a simple metric card."""
    val_str = str(value)
    if len(val_str) > 16:
        val_size = "1.0rem"
    elif len(val_str) > 8:
        val_size = "1.25rem"
    else:
        val_size = "1.45rem"

    st.markdown(f"""
    <div class="enterprise-card" style="border-top: 2px solid {accent_color};">
        <div>
            <div class="metric-label">{title}</div>
            <div class="metric-val" style="font-size: {val_size};">{value}</div>
        </div>
        <div class="metric-meta" style="color: {accent_color};">
            {meta}
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_pca_scatter_plot(df: pd.DataFrame) -> go.Figure:
    """Creates a clean 2D PCA cluster visualization."""
    color_map = {k: COLOR_PALETTE.get(k, '#94A3B8') for k in df['CareerCluster'].unique()}
    
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
            borderwidth=1
        ),
        xaxis=dict(gridcolor='rgba(255,255,255,0.06)', title='PCA Component 1'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.06)', title='PCA Component 2'),
        margin=dict(l=20, r=20, t=10, b=45)
    )
    return fig


def create_cluster_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a practical bar chart comparing key tenure and promotion averages by cluster."""
    grouped = df.groupby('CareerCluster')[['YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion']].mean().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['CareerCluster'],
        y=grouped['YearsAtCompany'].round(1),
        name='Avg Years at Company',
        marker_color='#818CF8'
    ))
    fig.add_trace(go.Bar(
        x=grouped['CareerCluster'],
        y=grouped['YearsInCurrentRole'].round(1),
        name='Avg Years in Current Role',
        marker_color='#38BDF8'
    ))
    fig.add_trace(go.Bar(
        x=grouped['CareerCluster'],
        y=grouped['YearsSinceLastPromotion'].round(1),
        name='Avg Years Since Promotion',
        marker_color='#FBBF24'
    ))

    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0', family='Inter', size=11),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(17, 23, 38, 0.8)'
        ),
        xaxis=dict(gridcolor='rgba(255,255,255,0.06)', title=''),
        yaxis=dict(gridcolor='rgba(255,255,255,0.06)', title='Years'),
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig


def create_stagnation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Generates department vs job role stagnation heatmap."""
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


def create_promotion_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a clean, readable histogram of years since last promotion."""
    fig = px.histogram(
        df,
        x='YearsSinceLastPromotion',
        color='PromotionGapRiskLevel',
        color_discrete_map={'Low Risk': '#34D399', 'Medium Risk': '#FBBF24', 'High Risk': '#FB7185'},
        nbins=16,
        title=""
    )
    fig.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0', family='Inter', size=11),
        xaxis=dict(gridcolor='rgba(255,255,255,0.06)', title='Years Since Last Promotion'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.06)', title='Employee Headcount'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(17, 23, 38, 0.8)'
        ),
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig


def create_manager_impact_chart(mgr_df: pd.DataFrame) -> go.Figure:
    """Creates manager tenure vs promotion gap chart."""
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
