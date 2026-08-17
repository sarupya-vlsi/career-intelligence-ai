"""
Automated Test Suite for Career Intelligence Platform
Tests Data Loader, Feature Engineering, ML Pipeline, Analytics, and Simulation
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import load_raw_data, engineer_features, get_full_processed_dataset
from src.ml_pipeline import CareerIntelligenceModel, CLUSTERING_FEATURES
from src.analytics import get_executive_kpis, get_role_stagnation_matrix, get_manager_insight_matrix


class TestCareerIntelligencePipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df_raw = load_raw_data()
        cls.df_processed = engineer_features(cls.df_raw)
        cls.ml_model = CareerIntelligenceModel(n_clusters=5, random_state=42)
        cls.df_clustered = cls.ml_model.fit_transform_dataset(cls.df_processed)

    def test_data_loading_and_shape(self):
        """Test dataset shape and non-empty rows."""
        self.assertEqual(len(self.df_raw), 1470)
        self.assertIn('EmployeeID', self.df_raw.columns)
        self.assertIn('YearsSinceLastPromotion', self.df_raw.columns)

    def test_feature_engineering_kpis(self):
        """Test engineered feature columns exist and have valid numerical ranges."""
        required_features = [
            'PromotionGapRatio', 'RoleStagnationIndex', 'TrainingIntensityScore',
            'ManagerStabilityIndicator', 'CareerVelocity', 'PromotionGapRiskScore',
            'PromotionGapRiskLevel', 'RetentionOpportunityIndex', 'RetentionPriorityLevel',
            'TrainingNeedIndicator', 'ManagerStabilityImpact', 'PrescriptiveAction'
        ]
        for feat in required_features:
            self.assertIn(feat, self.df_processed.columns, f"Feature {feat} missing in engineered dataset.")

        # Check score boundaries
        self.assertTrue((self.df_processed['PromotionGapRiskScore'] >= 0).all())
        self.assertTrue((self.df_processed['PromotionGapRiskScore'] <= 100).all())
        self.assertTrue((self.df_processed['RetentionOpportunityIndex'] >= 0).all())
        self.assertTrue((self.df_processed['RetentionOpportunityIndex'] <= 100).all())

    def test_ml_clustering_and_archetypes(self):
        """Test clustering fit, PCA reduction, and archetype mapping."""
        self.assertIn('ClusterID', self.df_clustered.columns)
        self.assertIn('CareerCluster', self.df_clustered.columns)
        self.assertIn('PCA1', self.df_clustered.columns)
        self.assertIn('PCA2', self.df_clustered.columns)
        self.assertIn('PCA3', self.df_clustered.columns)

        unique_clusters = self.df_clustered['CareerCluster'].nunique()
        self.assertGreaterEqual(unique_clusters, 4)

        # Check validation metrics
        self.assertIn('silhouette_kmeans', self.ml_model.metrics)
        self.assertGreater(self.ml_model.metrics['silhouette_kmeans'], 0.15)

    def test_single_employee_simulation(self):
        """Test simulation inference on modified employee features."""
        test_payload = {
            'TotalWorkingYears': 12,
            'YearsAtCompany': 8,
            'YearsInCurrentRole': 6,
            'YearsSinceLastPromotion': 5,
            'YearsWithCurrManager': 6,
            'JobLevel': 2,
            'TrainingTimesLastYear': 1,
            'PerformanceRating': 3,
            'JobSatisfaction': 2,
            'JobInvolvement': 3,
            'Attrition': 0,
            'PercentSalaryHike': 12
        }
        res = self.ml_model.predict_single(test_payload)
        self.assertIn('CareerCluster', res)
        self.assertIn('PromotionGapRiskScore', res)
        self.assertIn('RetentionOpportunityIndex', res)
        self.assertGreater(res['PromotionGapRiskScore'], 40.0)

        # Test intervention (give promotion & training)
        promoted_payload = {
            **test_payload,
            'YearsSinceLastPromotion': 0,
            'YearsInCurrentRole': 0,
            'JobLevel': 3,
            'TrainingTimesLastYear': 4
        }
        res_promoted = self.ml_model.predict_single(promoted_payload)
        self.assertLess(res_promoted['PromotionGapRiskScore'], res['PromotionGapRiskScore'])

    def test_analytics_kpi_calculations(self):
        """Test executive KPI calculations."""
        kpis = get_executive_kpis(self.df_clustered)
        self.assertEqual(kpis['total_employees'], 1470)
        self.assertGreater(kpis['active_employees'], 1000)
        self.assertGreater(kpis['high_promo_risk'], 0)

        role_matrix = get_role_stagnation_matrix(self.df_clustered)
        self.assertFalse(role_matrix.empty)

        mgr_matrix = get_manager_insight_matrix(self.df_clustered)
        self.assertFalse(mgr_matrix.empty)


if __name__ == '__main__':
    unittest.main()
