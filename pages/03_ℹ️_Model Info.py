import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from utils import column_1, column_2, feature_descriptions


# --------------------
# Page config
# --------------------
st.set_page_config(
    page_title='Churn Guard | About',
    layout='wide',
    page_icon='ℹ️'
)

# --------------------
# Load auth config
# --------------------
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Build authenticator (NOTE: no preauthorized argument anymore)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --------------------
# Render login form in sidebar
# --------------------
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

# --------------------
# Authenticated view
# --------------------
if authentication_status is True:
    authenticator.logout(location='sidebar', key='logout-button')

    # Hero header
    st.title("Model Information")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # left column info
        st.markdown(column_1)
        st.write("### 🔎 Feature Glossary")
        with st.expander("See model input definitions"):
            st.markdown(feature_descriptions)

    with col2:
        column_2

        st.write("### 🤖 App Pages")
        st.markdown(
            """
            - **📈 Dashboard:** KPIs and churn drivers across the whole customer base  
            - **🤖 Predict:** Real-time churn scoring for a single customer  
            - **📜 History:** Audit log of predictions (timestamp + result)
            """
        )

        

        # st.link_button(
        #     "View Project Repo on GitHub",
        #     url="https://github.com/coderacheal/Attrition-Meter",  # update this if you make a telecom-specific repo
        #     type="primary"
        # )

# --------------------
# Failed login
# --------------------
elif authentication_status is False:
    st.error("Username/password is incorrect.")

# --------------------
# Not logged in yet
# --------------------
else:
    st.info("Enter username and password to use the app.")
    st.code(
        """Test Account
Username: Group8
Password: Group8password"""
    )