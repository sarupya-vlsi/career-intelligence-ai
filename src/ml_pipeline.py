"""
Machine learning pipeline for workforce clustering and dimensionality reduction.
Uses K-Means clustering (validated with Hierarchical clustering and PCA).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score


CLUSTERING_FEATURES = [
    'TotalWorkingYears',
    'YearsAtCompany',
    'YearsInCurrentRole',
    'YearsSinceLastPromotion',
    'YearsWithCurrManager',
    'JobLevel',
    'PromotionGapRatio',
    'RoleStagnationIndex',
    'TrainingIntensityScore',
    'ManagerStabilityIndicator',
    'CareerVelocity',
    'PercentSalaryHike'
]

ARCHETYPE_DESCRIPTIONS = {
    'Fast-Track Performers': {
        'badge': 'Fast-Track Performer',
        'color': '#0EA5E9',
        'summary': 'Rapid career growth, frequent role changes, and low promotion delays.',
        'strategy': 'Provide high-visibility projects and leadership opportunities.'
    },
    'Stable Long-Term Contributors': {
        'badge': 'Stable Long-Term Contributor',
        'color': '#6366F1',
        'summary': 'High organizational tenure, solid domain expertise, and high retention stability.',
        'strategy': 'Involve in mentorship programs and subject matter expert tracks.'
    },
    'Early-Career Explorers': {
        'badge': 'Early-Career Explorer',
        'color': '#10B981',
        'summary': 'Lower company tenure, building foundational skills and looking for clear growth milestones.',
        'strategy': 'Set up structured 1-to-2 year progression milestones and mentorship.'
    },
    'Promotion-Stalled Employees': {
        'badge': 'Promotion-Stalled Employee',
        'color': '#F59E0B',
        'summary': 'Solid performers with 3+ years since their last promotion facing progression bottlenecks.',
        'strategy': 'Prioritize for promotion review, role scope expansion, or compensation adjustment.'
    },
    'High-Risk Stagnation Profiles': {
        'badge': 'High-Risk Stagnation Profile',
        'color': '#F43F5E',
        'summary': 'Long role tenure and prolonged manager continuity without upward or lateral movement.',
        'strategy': 'Consider lateral role rotation, manager change, or re-skilling.'
    }
}


class CareerIntelligenceModel:
    """
    K-Means clustering and PCA projection model for workforce segmentation.
    """
    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=15)
        self.hierarchical = AgglomerativeClustering(n_clusters=self.n_clusters)
        self.pca_2d = PCA(n_components=2, random_state=self.random_state)
        self.pca_3d = PCA(n_components=3, random_state=self.random_state)
        self.feature_names = CLUSTERING_FEATURES
        self.cluster_to_archetype_map: Dict[int, str] = {}
        self.is_fitted = False
        self.metrics: Dict[str, float] = {}

    def fit_transform_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fits clustering models on feature data and returns DataFrame with cluster labels and PCA coordinates.
        """
        data = df.copy()
        X = data[self.feature_names].values

        # Feature scaling
        X_scaled = self.scaler.fit_transform(X)

        # Fit K-Means
        kmeans_labels = self.kmeans.fit_predict(X_scaled)
        data['ClusterID'] = kmeans_labels

        # Fit Hierarchical clustering as a comparison baseline
        hierarchical_labels = self.hierarchical.fit_predict(X_scaled)
        data['HierarchicalClusterID'] = hierarchical_labels

        # Compute 2D and 3D PCA coordinates for plotting
        pca_2d_coords = self.pca_2d.fit_transform(X_scaled)
        data['PCA1'] = pca_2d_coords[:, 0].round(3)
        data['PCA2'] = pca_2d_coords[:, 1].round(3)

        pca_3d_coords = self.pca_3d.fit_transform(X_scaled)
        data['PCA3'] = pca_3d_coords[:, 2].round(3)

        # Record validation metrics
        self.metrics = {
            'silhouette_kmeans': float(silhouette_score(X_scaled, kmeans_labels)),
            'silhouette_hierarchical': float(silhouette_score(X_scaled, hierarchical_labels)),
            'calinski_harabasz': float(calinski_harabasz_score(X_scaled, kmeans_labels)),
            'davies_bouldin': float(davies_bouldin_score(X_scaled, kmeans_labels)),
            'pca_2d_variance': float(np.sum(self.pca_2d.explained_variance_ratio_)),
            'pca_3d_variance': float(np.sum(self.pca_3d.explained_variance_ratio_))
        }

        # Map cluster IDs to descriptive archetypes
        self.cluster_to_archetype_map = self._map_archetypes(data)
        data['CareerCluster'] = data['ClusterID'].map(self.cluster_to_archetype_map)

        self.is_fitted = True
        return data

    def _map_archetypes(self, df: pd.DataFrame) -> Dict[int, str]:
        """
        Assigns intuitive archetype names based on the centroid properties of each cluster.
        """
        cluster_means = df.groupby('ClusterID')[self.feature_names + ['PromotionGapRiskScore']].mean()
        assigned_map = {}
        unassigned_clusters = list(range(self.n_clusters))
        
        # 1. Early-Career: lowest company tenure
        early_cluster = cluster_means.loc[unassigned_clusters, 'YearsAtCompany'].idxmin()
        assigned_map[early_cluster] = 'Early-Career Explorers'
        unassigned_clusters.remove(early_cluster)

        # 2. Stable Long-Term: highest working years and company tenure
        veteran_cluster = cluster_means.loc[unassigned_clusters, 'TotalWorkingYears'].idxmax()
        assigned_map[veteran_cluster] = 'Stable Long-Term Contributors'
        unassigned_clusters.remove(veteran_cluster)

        # 3. High-Risk Stagnation: highest role stagnation index
        stagnant_cluster = cluster_means.loc[unassigned_clusters, 'RoleStagnationIndex'].idxmax()
        assigned_map[stagnant_cluster] = 'High-Risk Stagnation Profiles'
        unassigned_clusters.remove(stagnant_cluster)

        # 4. Promotion-Stalled: highest years since last promotion
        if unassigned_clusters:
            stalled_cluster = cluster_means.loc[unassigned_clusters, 'YearsSinceLastPromotion'].idxmax()
            assigned_map[stalled_cluster] = 'Promotion-Stalled Employees'
            unassigned_clusters.remove(stalled_cluster)

        # 5. Fast-Track: remaining cluster with frequent promotions
        for rem in unassigned_clusters:
            assigned_map[rem] = 'Fast-Track Performers'

        return assigned_map

    def predict_single(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts cluster assignment and calculates scores for an individual employee record.
        """
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted yet. Please run fit_transform_dataset first.")

        years_at_co = float(feature_dict.get('YearsAtCompany', 1))
        years_in_role = float(feature_dict.get('YearsInCurrentRole', 1))
        years_since_promo = float(feature_dict.get('YearsSinceLastPromotion', 0))
        years_with_mgr = float(feature_dict.get('YearsWithCurrManager', 1))
        total_working = float(feature_dict.get('TotalWorkingYears', 1))
        training_times = float(feature_dict.get('TrainingTimesLastYear', 2))
        job_level = float(feature_dict.get('JobLevel', 1))
        perf_rating = float(feature_dict.get('PerformanceRating', 3))
        job_sat = float(feature_dict.get('JobSatisfaction', 3))
        attrition = int(feature_dict.get('Attrition', 0))
        salary_hike = float(feature_dict.get('PercentSalaryHike', 15))

        promo_gap_ratio = years_since_promo / (years_at_co + 1.0)
        role_stagnation_idx = years_in_role / (years_at_co + 1.0)
        training_intensity = training_times / (years_at_co + 1.0)
        mgr_stability = years_with_mgr / (years_in_role + 1.0)
        career_velocity = job_level / (total_working + 1.0)

        vec = np.array([[
            total_working, years_at_co, years_in_role, years_since_promo,
            years_with_mgr, job_level, promo_gap_ratio, role_stagnation_idx,
            training_intensity, mgr_stability, career_velocity, salary_hike
        ]])

        scaled_vec = self.scaler.transform(vec)
        cluster_id = int(self.kmeans.predict(scaled_vec)[0])
        archetype = self.cluster_to_archetype_map.get(cluster_id, 'Fast-Track Performers')
        pca_coords = self.pca_2d.transform(scaled_vec)[0]

        # Calculate scores
        promo_years_weight = np.clip(years_since_promo / 10.0, 0, 1.0) * 35.0
        role_stagnation_weight = np.clip(role_stagnation_idx, 0, 1.0) * 25.0
        tenure_stagnation_weight = np.clip(years_in_role / 8.0, 0, 1.0) * 25.0
        satisfaction_drag = (1.0 - (job_sat / 4.0)) * 15.0
        pgrs = round(float(np.clip(promo_years_weight + role_stagnation_weight + tenure_stagnation_weight + satisfaction_drag, 0, 100)), 1)

        active_bonus = (1 - attrition) * 25.0
        perf_factor = (perf_rating / 4.0) * 25.0
        involvement_factor = (float(feature_dict.get('JobInvolvement', 3)) / 4.0) * 15.0
        stagnation_urgency = (pgrs / 100.0) * 35.0
        roi = round(float(np.clip(active_bonus + perf_factor + involvement_factor + stagnation_urgency, 0, 100)), 1)

        return {
            'ClusterID': cluster_id,
            'CareerCluster': archetype,
            'PCA1': float(pca_coords[0]),
            'PCA2': float(pca_coords[1]),
            'PromotionGapRiskScore': pgrs,
            'RetentionOpportunityIndex': roi,
            'PromotionGapRatio': round(promo_gap_ratio, 3),
            'RoleStagnationIndex': round(role_stagnation_idx, 3),
            'CareerVelocity': round(career_velocity, 3)
        }
