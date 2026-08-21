"""
Main pipeline execution script.
Runs data loading, feature engineering, K-Means clustering, and exports processed data and models.
"""

import os
import joblib
import pandas as pd
from src.data_loader import get_full_processed_dataset
from src.ml_pipeline import CareerIntelligenceModel
from src.analytics import get_executive_kpis


def run_pipeline():
    print("=" * 60)
    print("Workforce Promotion & Career Stagnation ML Pipeline")
    print("=" * 60)

    # 1. Load data and engineer features
    print("\n[1/3] Loading dataset and calculating career metrics...")
    df = get_full_processed_dataset()
    print(f"      Loaded {len(df)} records ({df.shape[1]} features).")

    # 2. Fit K-Means clustering model
    print("\n[2/3] Fitting K-Means clustering (K=5) and PCA...")
    model = CareerIntelligenceModel(n_clusters=5, random_state=42)
    processed_df = model.fit_transform_dataset(df)
    
    print(f"      Silhouette Score (K-Means): {model.metrics['silhouette_kmeans']:.4f}")
    print(f"      Calinski-Harabasz Score:    {model.metrics['calinski_harabasz']:.2f}")
    print(f"      PCA Explained Variance (3D): {model.metrics['pca_3d_variance']*100:.2f}%")

    # 3. Save outputs
    print("\n[3/3] Saving processed data and trained model...")
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    processed_data_path = "data/processed/panw_engineered_features.csv"
    processed_df.to_csv(processed_data_path, index=False)
    print(f"      Saved: {processed_data_path}")

    model_path = "models/career_intelligence_model.pkl"
    joblib.dump(model, model_path)
    print(f"      Saved: {model_path}")

    # Summary
    kpis = get_executive_kpis(processed_df)
    print("\n" + "-" * 50)
    print("Pipeline Summary:")
    print(f"- Total Employees:        {kpis['total_employees']}")
    print(f"- Active Employees:       {kpis['active_employees']}")
    print(f"- High Stagnation Risk:   {kpis['high_promo_risk']} ({kpis['high_promo_risk_pct']}%)")
    print(f"- Priority Action Queue:  {kpis['immediate_roi_interventions']}")
    print(f"- Avg Years Since Promo:  {kpis['avg_years_without_promo']} years")
    print("-" * 50)
    print("\nDone! To launch the dashboard, run: streamlit run app.py")


if __name__ == "__main__":
    run_pipeline()
