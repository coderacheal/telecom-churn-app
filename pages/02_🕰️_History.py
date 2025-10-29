import streamlit as st
import pandas as pd
import os


st.set_page_config(
    page_title="Prediction History",
    page_icon="📜",
    layout="wide"
)


st.title("📜Prediction History")
st.write("This page records churn predictions made in this session and across past runs.")

# 1. Load from session_state first
session_history = st.session_state.get("prediction_history", [])

# 2. Try to also load from CSV on disk (persistent history between runs)
csv_path = "prediction_history.csv"
file_history = []

if os.path.exists(csv_path):
    try:
        file_history = pd.read_csv(csv_path).to_dict(orient="records")
    except Exception:
        file_history = []


# 3. Merge both sources:
#    - file_history = what's saved on disk from previous runs
#    - session_history = what we just did this run
#    We combine them, newest last, and drop dupes by timestamp + MonthlyCharge as a simple proxy
combined_history = file_history + session_history
history_df = pd.DataFrame(combined_history)

if history_df.empty:
    st.info("No predictions have been logged yet. Go to the Predict page, make a prediction, then come back here.")
    st.stop()

# Drop exact duplicates if any
history_df = history_df.drop_duplicates(
    subset=["timestamp", "MonthlyCharge", "AccountWeeks", "prediction_raw"],
    keep="last"
)

# 4. KPIs summary row
st.markdown("### 📈 Summary")

total_preds = len(history_df)
churn_preds = (history_df["prediction_raw"] == 1).sum()
stay_preds = (history_df["prediction_raw"] == 0).sum()
churn_rate = (churn_preds / total_preds * 100) if total_preds > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Predictions Made", f"{total_preds}")
with col2:
    st.metric("Predicted as Churn", f"{churn_preds}")
with col3:
    st.metric("Predicted as Stay", f"{stay_preds}")
with col4:
    st.metric("Churn Prediction Rate", f"{churn_rate:.1f}%")

st.markdown("---")

# 5. Show the detailed history table
st.markdown("### 🧾 Detailed Log")

# reorder columns for readability
preferred_cols = [
    "timestamp",
    "prediction_label",
    "prediction_raw",
    "AccountWeeks",
    "MonthlyCharge",
    "CustServCalls",
    "DataUsage",
    "OverageFee",
    "RoamMins",
    "AvgCallDuration",
    "CostPerUsage",
    "ContractRenewal",
    "DataPlan",
    "DayMins",
    "DayCalls",
]

display_cols = [c for c in preferred_cols if c in history_df.columns]
display_df = history_df[display_cols].sort_values(by="timestamp", ascending=False)

# make it pretty
st.dataframe(
    display_df,
    use_container_width=True,
    height=400,
)

st.caption(
    "timestamp = when the prediction was made • "
    "prediction_label = model decision • "
    "CustServCalls / OverageFee are red flags for unhappy customers."
)
