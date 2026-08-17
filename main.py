"""
Main Pipeline Orchestrator & CLI Runner
Executes data ingestion, feature engineering, clustering pipeline, and persists processed artifacts.
"""

import os
import joblib
import pandas as pd
from src.data_loader import get_full_processed_dataset
from src.ml_pipeline import CareerIntelligenceModel
from src.analytics import get_executive_kpis, get_role_stagnation_matrix


def run_pipeline():
    print("=" * 70)
    print("PALO ALTO NETWORKS — CAREER INTELLIGENCE & RETENTION PIPELINE")
    print("=" * 70)

    # 1. Ingest and Engineer Features
    print("\n[1/4] Ingesting raw workforce data and engineering career KPIs...")
    df = get_full_processed_dataset()
    print(f"      Loaded {len(df)} employee records with {df.shape[1]} total attributes.")

    # 2. Fit Unsupervised Clustering & Validation
    print("\n[2/4] Fitting Unsupervised K-Means (K=5) & Hierarchical Clustering...")
    model = CareerIntelligenceModel(n_clusters=5, random_state=42)
    processed_df = model.fit_transform_dataset(df)
    
    print(f"      Clustering Metrics:")
    print(f"      - Silhouette Score (K-Means):      {model.metrics['silhouette_kmeans']:.4f}")
    print(f"      - Silhouette Score (Hierarchical): {model.metrics['silhouette_hierarchical']:.4f}")
    print(f"      - Calinski-Harabasz Index:         {model.metrics['calinski_harabasz']:.2f}")
    print(f"      - Cumulative PCA Variance (3D):    {model.metrics['pca_3d_variance']*100:.2f}%")

    # 3. Export Processed Data & Model Artifacts
    print("\n[3/4] Exporting processed dataset and model artifacts...")
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    processed_data_path = "data/processed/panw_engineered_features.csv"
    processed_df.to_csv(processed_data_path, index=False)
    print(f"      Saved processed dataset to '{processed_data_path}'")

    model_path = "models/career_intelligence_model.pkl"
    joblib.dump(model, model_path)
    print(f"      Serialized model pipeline to '{model_path}'")

    # 4. Generate Executive KPI Summary
    print("\n[4/4] Generating Executive Workforce Snapshot...")
    kpis = get_executive_kpis(processed_df)
    print("      " + "-" * 50)
    print(f"      Total Workforce Analyzed:          {kpis['total_employees']}")
    print(f"      Active Employees:                  {kpis['active_employees']}")
    print(f"      High Stagnation Risk Headcount:    {kpis['high_promo_risk']} ({kpis['high_promo_risk_pct']}%)")
    print(f"      Immediate Retention Priority:      {kpis['immediate_roi_interventions']}")
    print(f"      Mean Years Since Last Promotion:   {kpis['avg_years_without_promo']} yrs")
    print("      " + "-" * 50)

    print("\n>>> Pipeline execution completed successfully! <<<")
    print("Run `python -m streamlit run app.py` to launch the interactive web dashboard.")


if __name__ == "__main__":
    run_pipeline()
