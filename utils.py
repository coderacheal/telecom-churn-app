column_1 = """
### **The Goal**
###### To predict which customers are likely to leave (churn) and **explain why**, so the business can take action before losing revenue.

### 🔍 What this app does
- **Churn Prediction (Real-Time):**  
  Enter a single customer's usage, billing, and service behavior. The app calls a live machine learning model deployed on Azure ML and tells you if the customer is at risk of leaving.

- **Customer Health Dashboard:**  
  Visual KPIs and charts built from the telecom churn dataset.  
  We highlight patterns like:
  - High support call volume → higher churn
  - High overage fees → frustration → churn
  - Short tenure customers leaving early

- **Prediction History / Audit Trail:**  
  Every prediction you run is logged with timestamp, the inputs you sent, and the model’s decision (“Churn” or “Stay”).  
  This is one step toward monitoring model behavior over time (MLOps best practice).

### 🎯 Why churn matters
Keeping an existing customer is cheaper than acquiring a new one.  
If we can identify “who is at risk today,” retention teams can intervene with:
- plan adjustments,
- billing credits,
- win-back outreach.
"""

column_2 = """
### 🤖 The ML Model
- **Model type:** Random Forest classifier
- **Serving:** Deployed as an online endpoint in Azure Machine Learning
- **Interface:** REST API (secured with a key)

The model uses telecom behavior signals such as:
- **AccountWeeks** – how long they’ve been a customer  
- **ContractRenewal** – did they recently renew or are they about to lapse  
- **DataPlan / DataUsage** – are they using mobile data and how heavily  
- **CustServCalls** – how often they call support (pain indicator)  
- **MonthlyCharge / OverageFee** – are we charging them a lot  
- **RoamMins** – roaming behavior (can get expensive)  
- Engineered signals like **AvgCallDuration** and **CostPerUsage**

These get sent to the Azure endpoint, scored, and returned as:
- `1` → high churn risk ❌  
- `0` → likely to stay ✅  

### 🛠 MLOps / Engineering Highlights
- Data versioned (v1 / v2) for training
- Model registered and deployed to a managed online endpoint
- Streamlit app as the front-end for business users
- History page for lightweight monitoring

"""

feature_descriptions = """
**Feature Glossary (Inputs to the Model)**

- **AccountWeeks**  
  How long the customer has been active with the company (in weeks). Low tenure + high frustration = danger.

- **ContractRenewal (0/1)**  
  Whether the customer just renewed their plan. Customers who refuse to renew are churn risks.

- **DataPlan (0/1)**  
  Whether they have a data plan. Customers without a data plan sometimes churn faster.

- **DataUsage**  
  How much mobile data (GB) they actually consumed. Heavy users get price sensitive.

- **CustServCalls**  
  How many times they called customer service. More calls = more problems = higher churn.

- **DayMins / DayCalls**  
  How much they call during the day, and how often. Proxy for engagement.

- **MonthlyCharge**  
  Current monthly bill in dollars.

- **OverageFee**  
  Extra charges beyond their plan. This is a churn trigger.

- **RoamMins**  
  Minutes spent on roaming. Roaming is expensive and often causes bill shock.

- **AvgCallDuration**  
  (Engineered) Average minutes per call. Signals style of usage.

- **CostPerUsage**  
  (Engineered) A cost-efficiency signal — how expensive this customer’s usage is.

**Target: Churn**  
`1` = the customer left  
`0` = the customer stayed
"""
