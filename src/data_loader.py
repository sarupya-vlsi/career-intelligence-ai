"""
Data loading and feature engineering module.
Calculates career velocity, promotion gap ratios, and stagnation metrics.
"""

import os
import pandas as pd
import numpy as np


EXPECTED_COLUMNS = [
    'Age', 'Attrition', 'BusinessTravel', 'DailyRate', 'Department',
    'DistanceFromHome', 'Education', 'EducationField', 'EnvironmentSatisfaction',
    'Gender', 'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobRole',
    'JobSatisfaction', 'MaritalStatus', 'MonthlyIncome', 'MonthlyRate',
    'NumCompaniesWorked', 'OverTime', 'PercentSalaryHike', 'PerformanceRating',
    'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',
    'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany',
    'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager'
]


def load_raw_data(file_path: str = None) -> pd.DataFrame:
    """Loads the raw HR dataset from disk."""
    if file_path is None or not os.path.exists(file_path):
        candidate_paths = [
            "data/raw/Palo Alto Networks(1).csv",
            os.path.join(os.path.dirname(__file__), "..", "data", "raw", "Palo Alto Networks(1).csv"),
            "Palo Alto Networks(1).csv",
            os.path.join(os.path.dirname(__file__), "..", "Palo Alto Networks(1).csv"),
            os.path.join(os.getcwd(), "data", "raw", "Palo Alto Networks(1).csv"),
            os.path.join(os.getcwd(), "Palo Alto Networks(1).csv")
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                file_path = p
                break
    
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError("Could not locate dataset 'Palo Alto Networks(1).csv'. Please check the file path.")

    df = pd.read_csv(file_path)
    
    # Assign employee ID if missing
    if 'EmployeeID' not in df.columns:
        df.insert(0, 'EmployeeID', [f"PANW-{1000 + i}" for i in range(len(df))])
    
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes career progression, stagnation, and retention opportunity indicators.
    """
    data = df.copy()

    # Small constant to prevent zero-division
    EPSILON = 1.0

    # 1. Career velocity and stagnation ratios
    data['PromotionGapRatio'] = (data['YearsSinceLastPromotion'] / (data['YearsAtCompany'] + EPSILON)).round(3)
    data['RoleStagnationIndex'] = (data['YearsInCurrentRole'] / (data['YearsAtCompany'] + EPSILON)).round(3)
    data['TrainingIntensityScore'] = (data['TrainingTimesLastYear'] / (data['YearsAtCompany'] + EPSILON)).round(3)
    data['ManagerStabilityIndicator'] = (data['YearsWithCurrManager'] / (data['YearsInCurrentRole'] + EPSILON)).round(3)
    data['ManagerTenureRatio'] = (data['YearsWithCurrManager'] / (data['YearsAtCompany'] + EPSILON)).round(3)
    data['RolePromoGapDiff'] = (data['YearsInCurrentRole'] - data['YearsSinceLastPromotion'])

    # 2. Career velocity (advancement per total experience)
    data['CareerVelocity'] = (data['JobLevel'] / (data['TotalWorkingYears'] + EPSILON)).round(3)
    
    # Income compared to average for the role
    role_avg_income = data.groupby('JobRole')['MonthlyIncome'].transform('mean')
    data['CompRatioToRoleAvg'] = (data['MonthlyIncome'] / role_avg_income).round(2)

    # 3. Overall satisfaction average
    data['OverallSatisfaction'] = (
        (data['EnvironmentSatisfaction'] + data['JobSatisfaction'] + 
         data['RelationshipSatisfaction'] + data['WorkLifeBalance']) / 4.0
    ).round(2)

    # 4. Tenure career stages
    def get_career_stage(years):
        if years <= 2:
            return 'Early Stage (0-2 yrs)'
        elif years <= 6:
            return 'Growth Stage (3-6 yrs)'
        elif years <= 12:
            return 'Established Stage (7-12 yrs)'
        else:
            return 'Veteran Stage (13+ yrs)'
    
    data['CareerStage'] = data['YearsAtCompany'].apply(get_career_stage)

    # 5. Composite Promotion Gap Risk Score (0-100)
    promo_years_weight = np.clip(data['YearsSinceLastPromotion'] / 10.0, 0, 1.0) * 35.0
    role_stagnation_weight = np.clip(data['RoleStagnationIndex'], 0, 1.0) * 25.0
    tenure_stagnation_weight = np.clip(data['YearsInCurrentRole'] / 8.0, 0, 1.0) * 25.0
    satisfaction_drag = (1.0 - (data['JobSatisfaction'] / 4.0)) * 15.0

    raw_promo_risk = promo_years_weight + role_stagnation_weight + tenure_stagnation_weight + satisfaction_drag
    data['PromotionGapRiskScore'] = np.clip(raw_promo_risk, 0, 100).round(1)

    def categorize_promo_risk(score):
        if score >= 55.0:
            return 'High Risk'
        elif score >= 30.0:
            return 'Medium Risk'
        else:
            return 'Low Risk'

    data['PromotionGapRiskLevel'] = data['PromotionGapRiskScore'].apply(categorize_promo_risk)

    # 6. Retention Opportunity Index (0-100)
    # Highlights active high performers who are facing promotion delays
    active_bonus = (1 - data['Attrition']) * 25.0
    perf_factor = (data['PerformanceRating'] / 4.0) * 25.0
    involvement_factor = (data['JobInvolvement'] / 4.0) * 15.0
    stagnation_urgency = (data['PromotionGapRiskScore'] / 100.0) * 35.0

    raw_roi = active_bonus + perf_factor + involvement_factor + stagnation_urgency
    data['RetentionOpportunityIndex'] = np.clip(raw_roi, 0, 100).round(1)

    def categorize_roi(roi, attrition):
        if attrition == 1:
            return 'Already Attrited'
        elif roi >= 70.0:
            return 'Immediate Action'
        elif roi >= 50.0:
            return 'Watchlist'
        else:
            return 'Low Urgency'

    data['RetentionPriorityLevel'] = [
        categorize_roi(r, a) for r, a in zip(data['RetentionOpportunityIndex'], data['Attrition'])
    ]

    # 7. Training need classification
    def get_training_need(row):
        if row['TrainingTimesLastYear'] <= 1 and row['PromotionGapRiskScore'] >= 40:
            return 'High Development Need'
        elif row['TrainingTimesLastYear'] <= 2:
            return 'Moderate Development Need'
        else:
            return 'Sufficiently Trained'

    data['TrainingNeedIndicator'] = data.apply(get_training_need, axis=1)

    # 8. Manager continuity impact
    def get_manager_impact(row):
        if row['YearsWithCurrManager'] >= 5 and row['YearsSinceLastPromotion'] >= 4:
            return 'Prolonged Stagnant Manager Dyad'
        elif row['YearsWithCurrManager'] >= 4:
            return 'Stable Leadership Continuity'
        elif row['YearsWithCurrManager'] <= 1:
            return 'Recent Manager Transition'
        else:
            return 'Moderate Manager Continuity'

    data['ManagerStabilityImpact'] = data.apply(get_manager_impact, axis=1)

    # 9. Practical suggested action
    def generate_prescriptive_action(row):
        if row['Attrition'] == 1:
            return "Exit Analysis & Knowledge Transfer"
        elif row['PromotionGapRiskScore'] >= 60 and row['PerformanceRating'] >= 3:
            return "Promotion & Compensation Review"
        elif row['RoleStagnationIndex'] >= 0.6 and row['YearsInCurrentRole'] >= 4:
            return "Lateral Role Rotation / New Project"
        elif row['TrainingTimesLastYear'] <= 1:
            return "Upskilling & Training Program"
        elif row['ManagerStabilityImpact'] == 'Prolonged Stagnant Manager Dyad':
            return "Manager Mentorship & Skip-Level Check-in"
        else:
            return "Regular Annual Review"

    data['PrescriptiveAction'] = data.apply(generate_prescriptive_action, axis=1)

    return data


def get_full_processed_dataset(file_path: str = None) -> pd.DataFrame:
    """Loads raw data and runs feature engineering."""
    raw_df = load_raw_data(file_path)
    processed_df = engineer_features(raw_df)
    return processed_df
