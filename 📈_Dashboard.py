# import os
import yaml
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader


# Load auth config
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Build authenticator 
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Render login form in sidebar
authenticator.login(
    location='sidebar',
    fields={
        "Form name": "Login",
        "Username": "Username",
        "Password": "Password",
        "Login": "Login"
    }
)

# Pull auth state from session_state (this is how newer versions work)
authentication_status = st.session_state.get("authentication_status", None)
name = st.session_state.get("name", None)
username = st.session_state.get("username", None)

# PAGE CONFIG
st.set_page_config(
    page_title="Churn Dashboard",
    layout="wide",
    page_icon="📈"
)

# LOAD DATA (adjust path if needed)
def load_data():
    data_path = './data/telecom_churn_v2.csv'
    return pd.read_csv(data_path)

df = load_data()

# Churn is 0/1, we can map that to labels for plotting
df["ChurnLabel"] = df["Churn"].map({0: "Stayed", 1: "Churned"})


if authentication_status is True:
    authenticator.logout(location='sidebar', key='logout-button')
# SMALL HELPERS
    def kpi_card(title, value, subtitle=None):
        """Simple styled KPI card."""
        st.markdown(
            f"""
            <div style="
                background-color:#1f2937;
                border:1px solid #4b5563;
                border-radius:0.75rem;
                padding:1rem 1.25rem;
                color:#f9fafb;
                font-family:system-ui, sans-serif;
                line-height:1.4;
                min-height:110px;
            ">
                <div style="font-size:.8rem; color:#9ca3af; text-transform:uppercase; letter-spacing:0.05em;">
                    {title}
                </div>
                <div style="font-size:1.6rem; font-weight:600; margin-top:.25rem; color:#fff;">
                    {value}
                </div>
                <div style="font-size:.8rem; color:#9ca3af; margin-top:.5rem;">
                    {subtitle if subtitle else ""}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    def churn_rate(df):
        return (df["Churn"].mean()) * 100  

    def avg_tenure(df):
        return df["AccountWeeks"].mean()

    def avg_monthly_charge(df):
        return df["MonthlyCharge"].mean()

    def avg_custserv_calls(df):
        return df["CustServCalls"].mean()

    # -------------------------------------------------
    # KPI VIEW
    # -------------------------------------------------
    def show_kpi_overview():
        st.header("Churn KPIs")

        # KPI cards row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi_card(
                "Overall Churn Rate",
                f"{churn_rate(df):.1f}%",
                "Percent of customers who left"
            )
        with c2:
            kpi_card(
                "Avg Tenure",
                f"{avg_tenure(df):.1f} weeks",
                "How long they typically stay"
            )
        with c3:
            kpi_card(
                "Avg Monthly Charge",
                f"${avg_monthly_charge(df):.2f}",
                "Typical bill per user"
            )
        with c4:
            kpi_card(
                "Avg Support Calls",
                f"{avg_custserv_calls(df):.2f}",
                "Service pain signal"
            )

        st.markdown("---")

        # Row 2: churn breakdown pie + churn vs customer service calls
        r1c1, r1c2 = st.columns(2)

        with r1c1:
            st.markdown("#### Who is leaving?")
            churn_counts = df["ChurnLabel"].value_counts().reset_index()
            churn_counts.columns = ["Status", "Count"]

            fig_pie = px.pie(
                churn_counts,
                names="Status",
                values="Count",
                title="Stayed vs Churned",
                hole=0.4,
                height=480,
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

            st.caption("This gives leadership a fast answer: how bad is our churn problem?")

        with r1c2:
            st.markdown("#### Pain point: Support calls")
            # Average # of customer service calls by churn status
            support_by_churn = (
                df.groupby("ChurnLabel")["CustServCalls"]
                .mean()
                .reset_index()
                .rename(columns={"CustServCalls": "AvgCustServCalls"})
            )

            fig_support = px.bar(
                support_by_churn,
                x="ChurnLabel",
                y="AvgCustServCalls",
                title="Avg Customer Service Calls by Status",
                text="AvgCustServCalls",
                color="ChurnLabel",
                height=480,
                color_discrete_sequence=["#60a5fa", "#f87171"]
            )
            fig_support.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_support.update_layout(
                xaxis_title="Customer Outcome",
                yaxis_title="Avg # of Calls to Support"
            )
            st.plotly_chart(fig_support, use_container_width=True)

            st.caption("Churned customers usually call support more. This is an early warning signal for retention team.")

        st.markdown("---")

        # Row 3: Cost vs usage / behavior
        r2c1, r2c2 = st.columns(2)

        with r2c1:
            st.markdown("#### Are high-bill customers leaving?")
            fig_bill = px.scatter(
                df,
                x="MonthlyCharge",
                y="AccountWeeks",
                color="ChurnLabel",
                opacity=0.7,
                trendline="ols",
                title="Monthly Charge vs Tenure (colored by Churn)",
                labels={
                    "MonthlyCharge": "Monthly Charge ($)",
                    "AccountWeeks": "Tenure (weeks)"
                },
                color_discrete_map={
                    "Stayed": "#60a5fa",
                    "Churned": "#f87171"
                }
            )
            st.plotly_chart(fig_bill, use_container_width=True)

            st.caption(
                "Churners tend to have lower tenure. "
                "If you see churn inside the first X weeks at higher bills, pricing/onboarding might be a problem."
            )

        with r2c2:
            st.markdown("#### Roaming cost pressure")
            fig_roam = px.scatter(
                df,
                x="RoamMins",
                y="OverageFee",
                color="ChurnLabel",
                opacity=0.7,
                title="Roaming Minutes vs Overage Fees",
                labels={
                    "RoamMins": "Roaming Minutes",
                    "OverageFee": "Overage Fees ($)"
                },
                color_discrete_map={
                    "Stayed": "#60a5fa",
                    "Churned": "#f87171"
                }
            )
            st.plotly_chart(fig_roam, use_container_width=True)

            st.caption(
                "Customers who pay more in overage/roaming look more likely to leave. "
                "That's a pricing / plan design opportunity."
            )

        st.markdown("---")

        st.markdown("#### Operational Takeaways")
        st.write(
            """
            - 🔥 High support-call customers are at higher churn risk.  
            → Action: flag accounts with 3+ calls for proactive retention.
            
            - 💸 People paying more and staying a shorter time may feel overcharged early.  
            → Action: stabilize billing for new customers in first 3 months.

            - 🌍 Roaming + overage fees are pain points.  
            → Action: targeted plan recommendations for heavy roamers.

            This is where you talk to leadership. We're answering:  
            'Who is unhappy?', 'What makes them unhappy?', and 'Where do we intervene first?'
            """
        )


    # -------------------------------------------------
    # EDA / DEEP DIVE VIEW
    # -------------------------------------------------
    def show_eda_view():
        st.header("Deep Dive / EDA")

        # 1. Distribution of key numeric fields with churn overlay
        st.markdown("#### Usage and cost distributions")
        c1, c2, c3 = st.columns(3)

        with c1:
            fig_mins = px.histogram(
                df,
                x="DayMins",
                color="ChurnLabel",
                marginal="box",
                opacity=0.7,
                nbins=30,
                title="Daytime Minutes vs Churn"
            )
            st.plotly_chart(fig_mins, use_container_width=True)

        with c2:
            fig_calls = px.histogram(
                df,
                x="CustServCalls",
                color="ChurnLabel",
                barmode="group",
                nbins=10,
                title="Customer Service Calls Distribution"
            )
            st.plotly_chart(fig_calls, use_container_width=True)

        with c3:
            fig_charge = px.histogram(
                df,
                x="MonthlyCharge",
                color="ChurnLabel",
                nbins=30,
                opacity=0.7,
                title="Monthly Charge Distribution"
            )
            st.plotly_chart(fig_charge, use_container_width=True)

        st.caption(
            "These histograms show how churners behave vs non-churners across usage, support intensity, and billing."
        )

        st.markdown("---")

        # 2. Churn rate by whether they have a data plan
        st.markdown("#### Does having a data plan help retention?")
        if "DataPlan" in df.columns:
            churn_by_dataplan = (
                df.groupby("DataPlan")["Churn"]
                .mean()
                .reset_index()
            )
            churn_by_dataplan["DataPlanLabel"] = churn_by_dataplan["DataPlan"].map({0: "No Data Plan", 1: "Has Data Plan"})
            churn_by_dataplan["ChurnRatePct"] = churn_by_dataplan["Churn"] * 100

            fig_data_plan = px.bar(
                churn_by_dataplan,
                x="DataPlanLabel",
                y="ChurnRatePct",
                text="ChurnRatePct",
                title="Churn Rate by Data Plan Ownership (%)",
                color="DataPlanLabel",
                height=600,
                color_discrete_sequence=["#60a5fa", "#facc15"]
            )
            fig_data_plan.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_data_plan.update_layout(
                xaxis_title="Customer has a data plan?",
                yaxis_title="Churn Rate (%)",
                showlegend=False
            )
            st.plotly_chart(fig_data_plan, use_container_width=True)

            st.caption(
                "If churn is higher for 'No Data Plan', that means data plans might lock people in or deliver more value."
            )

        st.markdown("---")

        # 3. Correlation heatmap of numeric features
        st.markdown("#### Numeric Relationships (Correlation)")

        numeric_cols = df.select_dtypes(include=[np.number])
        corr = numeric_cols.corr().round(2)

        fig_corr = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            origin='lower',
            aspect="auto",
            height=600,
            title="Feature Correlation Heatmap"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        st.caption(
            "Higher DataUsage and DataPlan are strongly correlated (0.95), showing usage drives plan type. MonthlyCharge also correlates with usage (0.74–0.78), while Churn relates moderately with CustServCalls (0.21) and negatively with ContractRenewal (-0.26), suggesting service issues and lack of renewals contribute to churn."
        )


    # PAGE VIEW SWITCHER
    col_1, col_2 = st.columns(2)
    with col_1:
        pass
    with col_2:
        view = st.selectbox(
            "Choose dashboard view",
            options=["KPI Overview", "Deep Dive / EDA"],
            index=0
        )

    if view == "KPI Overview":
        show_kpi_overview()
    else:
        show_eda_view()


# Failed login
elif authentication_status is False:
    st.error("Username/password is incorrect.")

# Not logged in yet
else:
    st.info("Enter username and password to use the app.")
    st.code(
        """Test Account
Username: Group8
Password: Group8password"""
    )
