"""
Machine Learning Pipeline & Career Intelligence Modeling Module
Career Path Clustering, Dimensionality Reduction, Archetype Mapping, and Simulation
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
        'summary': 'Rapid career velocity, frequent role progression, and low promotion stagnation.',
        'strategy': 'Provide high-visibility strategic projects, executive sponsorship, and accelerated leadership pathways.'
    },
    'Stable Long-Term Contributors': {
        'badge': 'Stable Long-Term Contributor',
        'color': '#6366F1',
        'summary': 'Deep institutional knowledge, long organizational tenure, and high enterprise stability.',
        'strategy': 'Leverage for organizational mentorship, technical leadership, and continuous recognition.'
    },
    'Early-Career Explorers': {
        'badge': 'Early-Career Explorer',
        'color': '#10B981',
        'summary': 'Early organizational tenure, agile training participation, and foundational skill development.',
        'strategy': 'Structure clear 18-month career progression milestones, rotational exposure, and dedicated mentorship.'
    },
    'Promotion-Stalled Employees': {
        'badge': 'Promotion-Stalled Employee',
        'color': '#F59E0B',
        'summary': 'Moderate-to-high tenure with extended gaps since last promotion despite solid performance.',
        'strategy': 'Conduct urgent compensation & title review, establish immediate promotion milestone plans.'
    },
    'High-Risk Stagnation Profiles': {
        'badge': 'High-Risk Stagnation Profile',
        'color': '#F43F5E',
        'summary': 'Severe role stagnation and prolonged manager continuity without upward or lateral movement.',
        'strategy': 'Immediate talent intervention: lateral departmental rotation, manager realignment, or specialized re-skilling.'
    }
}


class CareerIntelligenceModel:
    """
    End-to-End Unsupervised Machine Learning Model for Workforce Career Intelligence.
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
        Fits clustering models on feature-engineered dataset and attaches:
        - ClusterID (0 to K-1)
        - CareerCluster (Human-readable Archetype)
        - HierarchicalClusterID (Validation benchmark)
        - PCA1, PCA2, PCA3 (Visual projections)
        """
        data = df.copy()
        X = data[self.feature_names].values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Fit K-Means
        kmeans_labels = self.kmeans.fit_predict(X_scaled)
        data['ClusterID'] = kmeans_labels

        # Fit Hierarchical for validation
        hierarchical_labels = self.hierarchical.fit_predict(X_scaled)
        data['HierarchicalClusterID'] = hierarchical_labels

        # Dimensionality Reduction
        pca_2d_coords = self.pca_2d.fit_transform(X_scaled)
        data['PCA1'] = pca_2d_coords[:, 0].round(3)
        data['PCA2'] = pca_2d_coords[:, 1].round(3)

        pca_3d_coords = self.pca_3d.fit_transform(X_scaled)
        data['PCA3'] = pca_3d_coords[:, 2].round(3)

        # Compute Clustering Metrics
        self.metrics = {
            'silhouette_kmeans': float(silhouette_score(X_scaled, kmeans_labels)),
            'silhouette_hierarchical': float(silhouette_score(X_scaled, hierarchical_labels)),
            'calinski_harabasz': float(calinski_harabasz_score(X_scaled, kmeans_labels)),
            'davies_bouldin': float(davies_bouldin_score(X_scaled, kmeans_labels)),
            'pca_2d_variance': float(np.sum(self.pca_2d.explained_variance_ratio_)),
            'pca_3d_variance': float(np.sum(self.pca_3d.explained_variance_ratio_))
        }

        # Dynamically map cluster centroids to business archetypes
        self.cluster_to_archetype_map = self._map_archetypes(data)
        data['CareerCluster'] = data['ClusterID'].map(self.cluster_to_archetype_map)

        self.is_fitted = True
        return data

    def _map_archetypes(self, df: pd.DataFrame) -> Dict[int, str]:
        """
        Analyzes cluster centroids across key dimensions to reliably assign standard archetypes.
        """
        cluster_means = df.groupby('ClusterID')[self.feature_names + ['PromotionGapRiskScore']].mean()
        assigned_map = {}
        unassigned_clusters = list(range(self.n_clusters))
        
        # 1. Early-Career Explorers: Lowest YearsAtCompany / Lowest TotalWorkingYears
        early_cluster = cluster_means.loc[unassigned_clusters, 'YearsAtCompany'].idxmin()
        assigned_map[early_cluster] = 'Early-Career Explorers'
        unassigned_clusters.remove(early_cluster)

        # 2. Stable Long-Term Contributors: Highest TotalWorkingYears and Highest YearsAtCompany
        veteran_cluster = cluster_means.loc[unassigned_clusters, 'TotalWorkingYears'].idxmax()
        assigned_map[veteran_cluster] = 'Stable Long-Term Contributors'
        unassigned_clusters.remove(veteran_cluster)

        # 3. High-Risk Stagnation Profiles: Highest RoleStagnationIndex among remaining
        stagnant_cluster = cluster_means.loc[unassigned_clusters, 'RoleStagnationIndex'].idxmax()
        assigned_map[stagnant_cluster] = 'High-Risk Stagnation Profiles'
        unassigned_clusters.remove(stagnant_cluster)

        # 4. Promotion-Stalled Employees: Highest YearsSinceLastPromotion or PromotionGapRatio among remaining
        if unassigned_clusters:
            stalled_cluster = cluster_means.loc[unassigned_clusters, 'YearsSinceLastPromotion'].idxmax()
            assigned_map[stalled_cluster] = 'Promotion-Stalled Employees'
            unassigned_clusters.remove(stalled_cluster)

        # 5. Fast-Track Performers: Remaining cluster(s) with high career velocity / promotion frequency
        for rem in unassigned_clusters:
            assigned_map[rem] = 'Fast-Track Performers'

        return assigned_map

    def predict_single(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts cluster archetype and calculates risk scores for an individual employee profile.
        """
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted yet. Fit with dataset first.")

        # Compute engineered features
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

        # Vector
        vec = np.array([[
            total_working, years_at_co, years_in_role, years_since_promo,
            years_with_mgr, job_level, promo_gap_ratio, role_stagnation_idx,
            training_intensity, mgr_stability, career_velocity, salary_hike
        ]])

        scaled_vec = self.scaler.transform(vec)
        cluster_id = int(self.kmeans.predict(scaled_vec)[0])
        archetype = self.cluster_to_archetype_map.get(cluster_id, 'Fast-Track Performers')
        pca_coords = self.pca_2d.transform(scaled_vec)[0]

        # Stagnation Risk Score
        p_weight = min(years_since_promo / 10.0, 1.0) * 35.0
        r_weight = min(role_stagnation_idx, 1.0) * 25.0
        t_weight = min(years_in_role / 8.0, 1.0) * 25.0
        s_drag = (1.0 - (job_sat / 4.0)) * 15.0
        promo_risk_score = round(min(max(p_weight + r_weight + t_weight + s_drag, 0.0), 100.0), 1)

        # Retention Opportunity Index (ROI)
        active_bonus = (1 - attrition) * 25.0
        p_factor = (perf_rating / 4.0) * 25.0
        involvement_factor = (float(feature_dict.get('JobInvolvement', 3)) / 4.0) * 15.0
        stagnation_urgency = (promo_risk_score / 100.0) * 35.0
        roi_score = round(min(max(active_bonus + p_factor + involvement_factor + stagnation_urgency, 0.0), 100.0), 1)

        return {
            'ClusterID': cluster_id,
            'CareerCluster': archetype,
            'PromotionGapRiskScore': promo_risk_score,
            'RetentionOpportunityIndex': roi_score,
            'PCA1': float(pca_coords[0]),
            'PCA2': float(pca_coords[1]),
            'ArchetypeInfo': ARCHETYPE_DESCRIPTIONS.get(archetype, {})
        }
