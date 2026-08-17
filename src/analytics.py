"""
Workforce Analytics & Prescriptive Intelligence Engine
Provides aggregation matrices, managerial insights, and executive summaries.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List


def get_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes top-level executive KPIs across workforce dataset.
    """
    total_employees = len(df)
    active_employees = int((df['Attrition'] == 0).sum())
    attrition_rate = (df['Attrition'].mean() * 100.0)
    
    high_promo_risk = int((df['PromotionGapRiskLevel'] == 'High Risk').sum())
    high_promo_risk_pct = (high_promo_risk / total_employees) * 100.0
    
    immediate_roi_interventions = int((df['RetentionPriorityLevel'] == 'Immediate Action').sum())
    immediate_roi_pct = (immediate_roi_interventions / max(active_employees, 1)) * 100.0
    
    avg_years_without_promo = float(df['YearsSinceLastPromotion'].mean())
    avg_role_tenure = float(df['YearsInCurrentRole'].mean())
    avg_company_tenure = float(df['YearsAtCompany'].mean())
    
    # Critical risk headcount in active workforce
    active_high_stagnation = int(((df['Attrition'] == 0) & (df['PromotionGapRiskLevel'] == 'High Risk')).sum())

    return {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'attrition_rate': round(attrition_rate, 1),
        'high_promo_risk': high_promo_risk,
        'high_promo_risk_pct': round(high_promo_risk_pct, 1),
        'immediate_roi_interventions': immediate_roi_interventions,
        'immediate_roi_pct': round(immediate_roi_pct, 1),
        'avg_years_without_promo': round(avg_years_without_promo, 2),
        'avg_role_tenure': round(avg_role_tenure, 2),
        'avg_company_tenure': round(avg_company_tenure, 2),
        'active_high_stagnation': active_high_stagnation
    }


def get_role_stagnation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates department and job role breakdown of career velocity, promotion gap, and risk scores.
    """
    role_stats = df.groupby(['Department', 'JobRole']).agg(
        Headcount=('EmployeeID', 'count'),
        AvgYearsAtCompany=('YearsAtCompany', 'mean'),
        AvgYearsInRole=('YearsInCurrentRole', 'mean'),
        AvgYearsSincePromo=('YearsSinceLastPromotion', 'mean'),
        AvgPromoRiskScore=('PromotionGapRiskScore', 'mean'),
        AvgRetentionOpportunityIndex=('RetentionOpportunityIndex', 'mean'),
        HighRiskPct=('PromotionGapRiskLevel', lambda s: (s == 'High Risk').mean() * 100.0),
        AttritionRate=('Attrition', lambda s: s.mean() * 100.0)
    ).reset_index()

    for col in ['AvgYearsAtCompany', 'AvgYearsInRole', 'AvgYearsSincePromo', 
                'AvgPromoRiskScore', 'AvgRetentionOpportunityIndex', 'HighRiskPct', 'AttritionRate']:
        role_stats[col] = role_stats[col].round(1)

    return role_stats.sort_values(by='AvgPromoRiskScore', ascending=False)


def get_manager_insight_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes leadership impact: manager tenure vs promotion gap and stagnation rates.
    """
    # Create Manager Tenure Bins
    df_copy = df.copy()
    bins = [-0.1, 1.0, 3.0, 6.0, 10.0, 40.0]
    labels = ['< 1 Year (New Dyad)', '1-3 Years', '4-6 Years', '7-10 Years', '10+ Years (Long Tenured)']
    df_copy['ManagerTenureBin'] = pd.cut(df_copy['YearsWithCurrManager'], bins=bins, labels=labels)

    mgr_stats = df_copy.groupby('ManagerTenureBin', observed=False).agg(
        EmployeeCount=('EmployeeID', 'count'),
        AvgYearsSincePromo=('YearsSinceLastPromotion', 'mean'),
        AvgRoleStagnationIndex=('RoleStagnationIndex', 'mean'),
        AvgPromoRiskScore=('PromotionGapRiskScore', 'mean'),
        AvgJobSatisfaction=('JobSatisfaction', 'mean'),
        StagnantDyadCount=('ManagerStabilityImpact', lambda s: (s == 'Prolonged Stagnant Manager Dyad').sum()),
        AttritionRate=('Attrition', lambda s: s.mean() * 100.0)
    ).reset_index()

    for col in ['AvgYearsSincePromo', 'AvgRoleStagnationIndex', 'AvgPromoRiskScore', 'AvgJobSatisfaction', 'AttritionRate']:
        mgr_stats[col] = mgr_stats[col].round(2)

    return mgr_stats


def get_archetype_radar_data(df: pd.DataFrame) -> Dict[str, List[float]]:
    """
    Prepares normalized radar metrics (0-100) for each career archetype.
    Dimensions:
    1. Career Velocity
    2. Promotion Recency (Inverted Promo Gap)
    3. Training Agility
    4. Organizational Loyalty (Tenure)
    5. Compensation Level
    6. Role Stability
    """
    archetypes = df['CareerCluster'].unique()
    radar_data = {}

    max_years_co = max(df['YearsAtCompany'].max(), 1)
    max_income = max(df['MonthlyIncome'].max(), 1)

    for arch in archetypes:
        subset = df[df['CareerCluster'] == arch]
        if len(subset) == 0:
            continue

        # 1. Velocity (0-100)
        v = float(np.clip(subset['CareerVelocity'].mean() * 200.0, 10, 100))
        # 2. Promotion Recency (100 - gap risk)
        p = float(np.clip(100.0 - subset['PromotionGapRiskScore'].mean(), 10, 100))
        # 3. Training Agility
        t = float(np.clip(subset['TrainingTimesLastYear'].mean() / 4.0 * 100.0, 10, 100))
        # 4. Loyalty (Tenure)
        l = float(np.clip(subset['YearsAtCompany'].mean() / max_years_co * 100.0 * 2.5, 10, 100))
        # 5. Compensation Level
        c = float(np.clip(subset['MonthlyIncome'].mean() / max_income * 100.0 * 1.5, 10, 100))
        # 6. Satisfaction
        s = float(np.clip(subset['OverallSatisfaction'].mean() / 4.0 * 100.0, 10, 100))

        radar_data[arch] = [round(x, 1) for x in [v, p, t, l, c, s]]

    return radar_data


def get_retention_priority_queue(df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    """
    Generates actionable priority queue of active employees requiring talent interventions.
    """
    active_df = df[df['Attrition'] == 0].copy()
    sorted_df = active_df.sort_values(by=['RetentionOpportunityIndex', 'PromotionGapRiskScore'], ascending=[False, False])
    
    output_cols = [
        'EmployeeID', 'JobRole', 'Department', 'CareerCluster', 'JobLevel',
        'YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion',
        'PerformanceRating', 'PromotionGapRiskScore', 'RetentionOpportunityIndex',
        'RetentionPriorityLevel', 'PrescriptiveAction'
    ]
    return sorted_df[output_cols].head(top_n)
