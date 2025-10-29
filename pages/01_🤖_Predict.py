import os
import streamlit as st
from typing import Dict
import pandas as pd
from datetime import datetime
from model_call import azure_model_rest_api_call

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    layout="wide",
    page_icon="🤖",
    page_title="Churn Guard | Predict"
)

class StreamlitApp:
    def __init__(self):
        # Title / description
        self.title = "Churn Guard"
        self.subtitle = "Telecom Customer Retention Intelligence · Powered by Azure ML · Live Inference API"

        # Default values for form inputs
        self.AccountWeeks = 40              # how long they've been a customer (weeks)
        self.ContractRenewal = 1            # 1 = yes, 0 = no
        self.DataPlan = 1                   # 1 = has data plan, 0 = no plan
        self.DataUsage = 5.0                # GB used
        self.CustServCalls = 2              # # calls to support
        self.DayMins = 250.0                # daytime call minutes
        self.DayCalls = 90                  # # daytime calls
        self.MonthlyCharge = 60.0           # monthly bill $
        self.OverageFee = 5.0               # overage fees $
        self.RoamMins = 8.0                 # roaming minutes
        self.AvgCallDuration = 2.8          # engineered feature (DayMins / DayCalls)
        self.CostPerUsage = 0.25            # engineered feature

    @staticmethod
    def format_data_for_the_api_call(
        AccountWeeks: int,
        ContractRenewal: int,
        DataPlan: int,
        DataUsage: float,
        CustServCalls: int,
        DayMins: float,
        DayCalls: int,
        MonthlyCharge: float,
        OverageFee: float,
        RoamMins: float,
        AvgCallDuration: float,
        CostPerUsage: float,
    ) -> Dict:
        """
        Build the request body in EXACT shape expected by your Azure inference service.
        This matches inference-script.py:
            data = json.loads(raw_data)["data"]
            for item in data: ...
        """
        request_body = {
            "data": [
                {
                    "AccountWeeks": AccountWeeks,
                    "ContractRenewal": ContractRenewal,
                    "DataPlan": DataPlan,
                    "DataUsage": DataUsage,
                    "CustServCalls": CustServCalls,
                    "DayMins": DayMins,
                    "DayCalls": DayCalls,
                    "MonthlyCharge": MonthlyCharge,
                    "OverageFee": OverageFee,
                    "RoamMins": RoamMins,
                    "AvgCallDuration": AvgCallDuration,
                    "CostPerUsage": CostPerUsage,
                }
            ]
        }
        return request_body

    def render_take_input(self) -> Dict:
        """
        Renders the form in Streamlit to collect inputs from the user.
        Returns a formatted request body ready for the API call.
        """
        st.title(self.title)
        st.caption(self.subtitle)
        st.markdown("---")

        st.subheader("📋 Customer Profile")

        col1, col2 = st.columns(2)

        with col1:
            input_AccountWeeks = st.number_input(
                "Account Weeks (tenure with company)",
                min_value=0,
                max_value=500,
                value=self.AccountWeeks,
                help="How long this customer has been active (in weeks).",
            )

            input_ContractRenewal = st.selectbox(
                "Contract Renewal?",
                options=[1, 0],
                index=0 if self.ContractRenewal == 1 else 1,
                help="1 = they recently renewed, 0 = they did not renew.",
            )

            input_DataPlan = st.selectbox(
                "Has Data Plan?",
                options=[1, 0],
                index=0 if self.DataPlan == 1 else 1,
                help="1 = has a data plan, 0 = no data plan.",
            )

            input_DataUsage = st.number_input(
                "Data Usage (GB)",
                min_value=0.0,
                max_value=1000.0,
                value=self.DataUsage,
                step=0.1,
                help="How much mobile data they actually used.",
            )

            input_CustServCalls = st.number_input(
                "Customer Service Calls (#)",
                min_value=0,
                max_value=50,
                value=self.CustServCalls,
                help="How many times they called support.",
            )

            input_DayMins = st.number_input(
                "Daytime Minutes Used",
                min_value=0.0,
                max_value=1000.0,
                value=self.DayMins,
                step=1.0,
                help="Total minutes of daytime calling.",
            )

        with col2:
            input_DayCalls = st.number_input(
                "Number of Daytime Calls",
                min_value=0,
                max_value=500,
                value=self.DayCalls,
                help="How many calls were made during the day.",
            )

            input_MonthlyCharge = st.number_input(
                "Monthly Charge ($)",
                min_value=0.0,
                max_value=500.0,
                value=self.MonthlyCharge,
                step=0.5,
                help="How much they pay per month.",
            )

            input_OverageFee = st.number_input(
                "Overage Fee ($)",
                min_value=0.0,
                max_value=500.0,
                value=self.OverageFee,
                step=0.5,
                help="How much they were charged in overages.",
            )

            input_RoamMins = st.number_input(
                "Roaming Minutes",
                min_value=0.0,
                max_value=500.0,
                value=self.RoamMins,
                step=1.0,
                help="Minutes spent roaming.",
            )

            input_AvgCallDuration = st.number_input(
                "Avg Call Duration (mins per call)",
                min_value=0.0,
                max_value=60.0,
                value=self.AvgCallDuration,
                step=0.1,
                help="Engineered: DayMins / DayCalls",
            )

            input_CostPerUsage = st.number_input(
                "Cost Per Usage ($ per unit)",
                min_value=0.0,
                max_value=10.0,
                value=self.CostPerUsage,
                step=0.01,
                help="Engineered cost efficiency feature for this customer.",
            )

        st.markdown("---")

        formatted_data = StreamlitApp.format_data_for_the_api_call(
            AccountWeeks=input_AccountWeeks,
            ContractRenewal=int(input_ContractRenewal),
            DataPlan=int(input_DataPlan),
            DataUsage=float(input_DataUsage),
            CustServCalls=int(input_CustServCalls),
            DayMins=float(input_DayMins),
            DayCalls=float(input_DayCalls),
            MonthlyCharge=float(input_MonthlyCharge),
            OverageFee=float(input_OverageFee),
            RoamMins=float(input_RoamMins),
            AvgCallDuration=float(input_AvgCallDuration),
            CostPerUsage=float(input_CostPerUsage),
        )

        return formatted_data

    def call_model_and_display(self, formatted_data: Dict):
        """
        Calls the deployed Azure ML model and displays the result.
        Also logs the prediction to session_state and to prediction_history.csv
        so we can show it on the History page.
        """
        if st.button("🔮 Predict Churn", type="primary"):
            # Call model and handle errors gracefully
            try:
                with st.spinner("Contacting churn model in Azure..."):
                    model_output = azure_model_rest_api_call(formatted_data)
            except RuntimeError as e:
                st.error(str(e))
                return

            # Parse model response
            predicted_outcomes = model_output.get("predictedOutcomes", [])
            user_inputs_echo = model_output.get("inputFeatures", [])

            if not predicted_outcomes:
                st.error("No prediction returned from model.")
                return

            pred = predicted_outcomes[0]  # 0 or 1
            churn_label = "Churn" if pred == 1 else "Stay"

            st.subheader("📌 Prediction Result")
            st.write(
                f"**Model Prediction:** {'Likely to CHURN ❌' if pred == 1 else 'Likely to STAY ✅'}"
            )

            if pred == 1:
                st.error("Alert: This customer is high-risk. Consider retention outreach ASAP.")
            else:
                st.success("This customer appears stable.")

            with st.expander("View model inputs sent to API"):
                st.json(user_inputs_echo)

            # Build log entry
            sent_row = formatted_data["data"][0]

            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "prediction_raw": int(pred),
                "prediction_label": churn_label,
                "AccountWeeks": sent_row["AccountWeeks"],
                "ContractRenewal": sent_row["ContractRenewal"],
                "DataPlan": sent_row["DataPlan"],
                "DataUsage": sent_row["DataUsage"],
                "CustServCalls": sent_row["CustServCalls"],
                "DayMins": sent_row["DayMins"],
                "DayCalls": sent_row["DayCalls"],
                "MonthlyCharge": sent_row["MonthlyCharge"],
                "OverageFee": sent_row["OverageFee"],
                "RoamMins": sent_row["RoamMins"],
                "AvgCallDuration": sent_row["AvgCallDuration"],
                "CostPerUsage": sent_row["CostPerUsage"],
            }

            # Initialize session_state history list if not present
            if "prediction_history" not in st.session_state:
                st.session_state["prediction_history"] = []

            # Append to in-memory history
            st.session_state["prediction_history"].append(log_entry)

            # Write to CSV for persistence
            history_df = pd.DataFrame(st.session_state["prediction_history"])
            # Make sure the directory exists before saving
            history_df.to_csv("prediction_history.csv", index=False)

            st.success("Prediction logged to history ✅")

# Streamlit entry
if __name__ == "__main__":
    app = StreamlitApp()
    formatted_data = app.render_take_input()
    app.call_model_and_display(formatted_data)
