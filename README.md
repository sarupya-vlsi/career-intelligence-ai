# Employee Promotion & Career Stagnation Analysis
### Machine Learning & People Analytics Project | Unified Mentor Internship

**Author:** Sarupya Guha (Intern ID: `UMID150826105831`)  
**Domain:** Applied Machine Learning & HR Analytics  
**Case Study:** Palo Alto Networks Workforce Dataset  

---

## Overview

Most traditional employee turnover analyses focus strictly on predicting **who will quit**. However, by the time an employee is ready to leave, it is often too late to retain them.

This project takes a proactive approach: **analyzing internal career progression, promotion delays, and role stagnation** using unsupervised machine learning. By identifying which employees are stalled in their careers despite good performance, HR and team managers can step in with timely promotions, lateral moves, or training before disengagement happens.

---

## Key Questions Addressed

1. **How long do employees stay in a single role before leaving?**
2. **Does a long promotion gap directly increase attrition risk?**
3. **How does manager continuity affect employee growth?** (e.g., staying under the same manager for 6+ years without a role change)
4. **Can we group employees into practical career profiles using clustering?**
5. **How can HR test the impact of promotions or upskilling using an interactive dashboard?**

---

## Features & Derived Metrics

From the standard 1,470-employee workforce dataset, we engineered several intuitive career health indicators:

- **Promotion Gap Ratio ($PGR$):** $\frac{\text{YearsSinceLastPromotion}}{\text{YearsAtCompany} + 1}$ — Proportion of time spent at the company without a promotion.
- **Role Stagnation Index ($RSI$):** $\frac{\text{YearsInCurrentRole}}{\text{YearsAtCompany} + 1}$ — Measures how long someone has stayed in their exact current position.
- **Training Intensity Score ($TIS$):** $\frac{\text{TrainingTimesLastYear}}{\text{YearsAtCompany} + 1}$ — Annual training and upskilling investment.
- **Manager Stability Indicator ($MSI$):** $\frac{\text{YearsWithCurrManager}}{\text{YearsInCurrentRole} + 1}$ — Ratio of manager tenure to current role tenure.
- **Career Velocity ($CV$):** $\frac{\text{JobLevel}}{\text{TotalWorkingYears} + 1}$ — Rate of title advancement relative to overall experience.
- **Promotion Gap Risk Score (0–100):** A composite score highlighting employees facing promotion bottlenecks and stagnation.
- **Retention Opportunity Index (0–100):** Prioritizes active, high-performing employees who are stalled and need immediate career intervention.

---

## Machine Learning Approach: Career Archetypes

We applied **StandardScaler normalization** and **K-Means Clustering ($K=5$)** (validated with Hierarchical Clustering and PCA) to group the workforce into five realistic profiles:

1. **Fast-Track Performers (~18%):** Rapid career growth, high velocity, and frequent promotions.
2. **Stable Long-Term Contributors (~16%):** Experienced senior employees with high stability and deep company knowledge.
3. **Early-Career Explorers (~23%):** Newer team members building foundational skills and looking for clear career milestones.
4. **Promotion-Stalled Employees (~27%):** High performers with 3+ years since their last promotion — the primary group at risk of voluntary turnover.
5. **High-Risk Stagnation Profiles (~15%):** Employees with multi-year role immobility under the same manager without advancement.

---

## Project Structure

```
├── data/
│   ├── raw/
│   │   └── Palo Alto Networks(1).csv      # Raw dataset (1,470 records)
│   └── processed/
│       └── panw_engineered_features.csv   # Dataset with engineered KPIs & clusters
├── docs/
│   └── RESEARCH_PAPER.md                  # Project research report & analysis notes
├── models/
│   └── career_intelligence_model.pkl      # Saved K-Means & PCA model pipeline
├── notebooks/
│   └── 01_exploratory_data_analysis_and_clustering.ipynb # EDA and model experiments
├── reports/
│   ├── RESEARCH_PAPER.tex                 # XeLaTeX project report source
│   └── RESEARCH_PAPER.pdf                 # Compiled project report PDF
├── src/
│   ├── data_loader.py                     # Data loading & feature calculation
│   ├── ml_pipeline.py                     # K-Means clustering, PCA, and prediction logic
│   ├── analytics.py                       # Aggregations, department breakdowns, metrics
│   └── ui_components.py                   # Plotly chart helpers and clean UI styling
├── tests/
│   └── test_pipeline.py                   # Unit tests for data loading & ML pipeline
├── app.py                                 # Streamlit web dashboard
├── main.py                                # Pipeline execution script
├── requirements.txt                       # Python dependencies
└── README.md
```


