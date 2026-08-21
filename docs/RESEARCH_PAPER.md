# Career Progression & Stagnation Analysis: An Unsupervised Learning Study for Employee Retention

**Author:** Sarupya Guha (Intern ID: `UMID150826105831`)  
**Domain:** Applied Machine Learning & HR Analytics  
**Organization:** Unified Mentor Internship Program  
**Case Study Dataset:** Palo Alto Networks Workforce Dataset  
**Date:** August 2026  

---

## Abstract

Predicting employee turnover is a common application of machine learning in Human Resources. However, most existing approaches use binary classification models to predict whether an employee will leave or stay. In practice, once an employee shows strong signals of leaving, it is often too late for an organization to retain them.

This study explores a proactive alternative: analyzing internal career velocity, promotion delays, and role stagnation using unsupervised machine learning. By examining a dataset of 1,470 employees from Palo Alto Networks, we engineer domain-specific career metrics—including the Promotion Gap Ratio, Role Stagnation Index, Manager Stability Indicator, and Career Velocity. 

Using K-Means clustering ($K=5$) and Principal Component Analysis (PCA), we group employees into five distinct career archetypes: Fast-Track Performers, Stable Long-Term Contributors, Early-Career Explorers, Promotion-Stalled Employees, and High-Risk Stagnation Profiles. Our findings show that approximately 27% of employees experience substantial promotion delays ($\ge 3.5$ years) despite solid performance, representing a primary group at risk of voluntary departure. We present an interactive Streamlit dashboard and scenario simulator to help managers explore these patterns and test retention interventions.

---

## 1. Introduction

### 1.1 Problem Context
Employee turnover carries substantial direct and indirect costs for technology organizations, including recruiting expenses, onboarding ramp time, and loss of domain knowledge. Traditional HR analytics tools typically focus on reactive turnover prediction:

$$\hat{y} \in \{0, 1\} \quad (1 = \text{Leaves}, 0 = \text{Stays})$$

While this classification identifies flight risk, it does not explain the underlying career progression issues that lead to disengagement in the first place. When an employee feels that their career is stalled—due to a long gap since their last promotion, prolonged tenure in the same role, or lack of training—they become much more likely to seek opportunities elsewhere.

### 1.2 Research Goals
The goals of this project are:
1. **Feature Engineering:** Derive meaningful metrics that capture promotion latency, role tenure relative to total company tenure, and manager continuity.
2. **Unsupervised Clustering:** Segment the workforce into interpretable career archetypes using K-Means and compare with Hierarchical clustering.
3. **Dimensionality Reduction:** Use PCA (2D and 3D) to visualize workforce career distributions.
4. **Actionable Prioritization:** Develop a simple scoring mechanism to highlight active high performers who are facing career stagnation.
5. **Interactive Tooling:** Build a Streamlit web application allowing HR professionals to explore data, view department trends, and simulate promotion and training scenarios.

---

## 2. Dataset & Feature Engineering

### 2.1 Dataset Summary
The study uses a workforce dataset consisting of 1,470 employee records with 31 original features covering demographics, job roles, satisfaction ratings, and tenure metrics.

| Metric / Attribute | Value |
| :--- | :--- |
| Total Employees ($N$) | 1,470 |
| Active Employees | 1,233 (83.9%) |
| Historical Attrition | 237 (16.1%) |
| Average Age | 36.9 years |
| Average Company Tenure | 7.0 years |
| Average Years in Role | 4.2 years |
| Average Years Since Last Promotion | 2.2 years |
| Average Years with Manager | 4.1 years |

### 2.2 Engineered Indicators
To quantify career health, several ratios and composite scores were computed (using a smoothing constant $\epsilon = 1.0$ to prevent division by zero):

1. **Promotion Gap Ratio ($PGR$):**
   $$PGR = \frac{\text{YearsSinceLastPromotion}}{\text{YearsAtCompany} + 1}$$
   Measures the fraction of total tenure spent waiting for a promotion.

2. **Role Stagnation Index ($RSI$):**
   $$RSI = \frac{\text{YearsInCurrentRole}}{\text{YearsAtCompany} + 1}$$
   Measures how long an employee has been in their current position relative to their company tenure.

3. **Training Intensity Score ($TIS$):**
   $$TIS = \frac{\text{TrainingTimesLastYear}}{\text{YearsAtCompany} + 1}$$

4. **Manager Stability Indicator ($MSI$):**
   $$MSI = \frac{\text{YearsWithCurrManager}}{\text{YearsInCurrentRole} + 1}$$

5. **Career Velocity ($CV$):**
   $$CV = \frac{\text{JobLevel}}{\text{TotalWorkingYears} + 1}$$

6. **Promotion Gap Risk Score (0–100):**
   A weighted composite index combining promotion gap years, role stagnation, tenure, and job satisfaction.

7. **Retention Opportunity Index (0–100):**
   An indicator designed to highlight active (non-attrited) employees who have high performance ratings but high stagnation risk scores.

---

## 3. Methodology & Unsupervised Clustering

### 3.1 Feature Scaling and Model Selection
The 12 career features were standardized using `StandardScaler`. We evaluated cluster solutions with $K \in [3, 8]$ using silhouette analysis and the elbow method, determining that $K=5$ provided the most balanced and interpretable segmentation of career stages.

### 3.2 Identified Career Archetypes

1. **Fast-Track Performers (18.4%, $n=270$):**
   - High career velocity, frequent title progression, low promotion gap.
   - Recommended strategy: High-impact projects and leadership development.

2. **Stable Long-Term Contributors (16.2%, $n=238$):**
   - Long total tenure, high domain experience, very low turnover risk.
   - Recommended strategy: Technical mentorship roles and subject matter expertise tracks.

3. **Early-Career Explorers (23.1%, $n=340$):**
   - Low company tenure, actively participating in training.
   - Recommended strategy: Structured 1-to-2 year milestones and onboarding mentorship.

4. **Promotion-Stalled Employees (27.3%, $n=401$):**
   - Solid performers with 3.5+ years since their last promotion.
   - Recommended strategy: Immediate promotion review, scope expansion, or compensation evaluation.

5. **High-Risk Stagnation Profiles (15.0%, $n=221$):**
   - High role stagnation ratio and prolonged tenure under the same manager without movement.
   - Recommended strategy: Lateral role transfer, project rotation, or manager realignment.

---

## 4. Key Findings

1. **Stagnation Precedes Attrition:** Over 27% of active employees are in the "Promotion-Stalled" cluster. In historical records, employees who spent more than 4 years in the same role without promotion exhibited significantly higher turnover rates.
2. **Managerial Continuity Bottlenecks:** Employees who remained with the same manager for 6+ years without a role change had higher average stagnation scores and lower reported job satisfaction.
3. **Training Engagement:** Employees who attended 3 or more training sessions per year showed higher internal mobility rates compared to those with 0–1 sessions.

---

## 5. Dashboard Implementation

An interactive Streamlit web dashboard (`app.py`) was developed to allow non-technical stakeholders to explore the findings:
- **Executive Overview:** High-level headcount, risk rates, and department breakdowns.
- **Cluster Explorer:** 2D and 3D PCA scatter plots, radar charts, and archetype profiles.
- **Promotion Gap Monitor:** Department-level heatmaps and role-level tenure statistics.
- **Action Queue:** Filterable roster of high-performing employees flagged for career review.
- **Scenario Simulator:** A what-if tool allowing managers to simulate promotions or training and see the resulting score and cluster shifts in real time.

---

## 6. Conclusion & Recommendations

By shifting focus from reactive churn forecasting to proactive career progression monitoring, organizations can identify career stagnation early. The combination of simple domain metrics and unsupervised clustering provides an interpretable and practical framework for talent retention.

---

## References

1. Boxall, P., & Purcell, J. (2016). *Strategy and Human Resource Management*. Palgrave Macmillan.
2. Scikit-learn Documentation: *Clustering and Principal Component Analysis*.
3. Allen, D. G., Bryant, P. C., & Vardaman, J. M. (2010). Retaining Talent: Replacing Misconceptions with Evidence-Based Strategies. *Academy of Management Perspectives*.
