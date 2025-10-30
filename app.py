import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import smtplib
from email.mime.text import MIMEText
import os

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------
st.set_page_config(
    page_title="AI Fraud Detection System",
    layout="wide",
)

# --------------------------------
# CUSTOM STYLES
# --------------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #e8e8e8;
    font-family: 'Poppins', sans-serif;
}
.main {
    background-color: #161a23;
    padding: 2.5rem;
    border-radius: 15px;
    box-shadow: 0 0 20px rgba(0,0,0,0.4);
}
h1 {
    color: #00b4d8;
    text-align: center;
    font-size: 2.3rem !important;
    letter-spacing: 1px;
}
h2, h3, h4 {
    color: #9ad9ea !important;
    font-weight: 600;
}
.stButton>button {
    background-color: #00b4d8;
    color: white;
    border: none;
    padding: 0.6rem 1.3rem;
    border-radius: 10px;
    font-size: 16px;
    transition: 0.3s ease-in-out;
}
.stButton>button:hover {
    background-color: #0077b6;
    transform: scale(1.03);
}
[data-testid="stMetricValue"] {
    color: #00d4ff;
    font-weight: bold;
    font-size: 1.4rem;
}
input, select, textarea {
    background-color: #1f2630 !important;
    color: white !important;
    border-radius: 8px !important;
    border: 1px solid #333 !important;
}
.stDownloadButton>button {
    background-color: #2a9d8f;
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1.3rem;
    border: none;
}
.stDownloadButton>button:hover {
    background-color: #21867a;
    transform: scale(1.02);
}
hr {
    border: 0.5px solid #2a2d3b;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------
# PAGE TITLE
# --------------------------------
st.title("AI Fraud Detection System")
st.markdown("<p style='text-align:center; font-size:16px;'>An intelligent system for identifying fraudulent transactions in real-time using AI.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --------------------------------
# EMAIL ALERT FUNCTION
# --------------------------------
def send_email_alert(summary_message, high_risk_count):
    try:
        msg = MIMEText(summary_message)
        msg['Subject'] = f"Fraud Alert - {high_risk_count} High-Risk Transactions"
        msg['From'] = "ganeshpatne044@gmail.com"
        msg['To'] = "ganeshpatne044@gmail.com"

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login("ganeshpatne044@gmail.com", "your_app_password")  # Replace with your app password
            server.send_message(msg)
    except Exception as e:
        st.warning(f"Email alert could not be sent: {e}")

# --------------------------------
# MODEL LOADING OR TRAINING
# --------------------------------
@st.cache_resource
def load_or_train_model():
    os.makedirs("model", exist_ok=True)
    try:
        model = joblib.load("model/fraud_model.pkl")
        return model
    except:
        df = pd.read_csv("data/creditcard.csv")

        if df.empty:
            st.error("Dataset is empty. Please check data/creditcard.csv.")
            return None

        df = df.sample(n=min(10000, len(df)), random_state=42)
        df = df.select_dtypes(include=[np.number])

        if 'Class' not in df.columns:
            st.warning("'Class' column missing. Creating dummy labels.")
            df['Class'] = np.random.randint(0, 2, len(df))

        X = df.drop('Class', axis=1)
        y = df['Class']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        joblib.dump(model, "model/fraud_model.pkl")
        return model

model = load_or_train_model()
if model is None:
    st.stop()

# --------------------------------
# FILE UPLOAD SECTION
# --------------------------------
st.subheader("Upload Transactions CSV")

uploaded_file = st.file_uploader("Upload a CSV file to analyze transactions", type=["csv"])

if uploaded_file is not None:
    df_new = pd.read_csv(uploaded_file)

    if df_new.empty:
        st.error("Uploaded file is empty.")
    else:
        st.write("Preview of Uploaded Data:")
        st.dataframe(df_new.head())

        if st.button("Predict Fraudulent Transactions"):
            X_new = df_new.select_dtypes(include=[np.number])
            X_new = X_new.drop('Class', axis=1, errors='ignore')

            if X_new.empty:
                st.error("No numeric columns found for prediction.")
            else:
                fraud_probabilities = model.predict_proba(X_new)[:, 1]
                predictions = (fraud_probabilities > 0.5).astype(int)

                df_new['Fraud_Probability'] = fraud_probabilities
                df_new['Fraud_Prediction'] = predictions

                st.success("Prediction Complete")
                st.dataframe(df_new.head(10))

                # ---- BATCH EMAIL ALERT ----
                high_risk_txns = df_new[df_new['Fraud_Probability'] > 0.9]

                if not high_risk_txns.empty:
                    st.warning(f"⚠️ {len(high_risk_txns)} High-Risk Transactions Detected (Probability > 0.9)")
                    st.dataframe(high_risk_txns[['Amount', 'Fraud_Probability']].head(10))

                    # Prepare summary email message
                    summary_message = f"""
ALERT: {len(high_risk_txns)} High-Risk Transactions Detected by AI Fraud Detection System

Transaction ID | Amount | Risk Score
------------------------------------
"""
                    for idx, row in high_risk_txns.iterrows():
                        summary_message += f"{idx:<15} | ₹{row.get('Amount', 0):<8} | {row['Fraud_Probability']:.2f}\n"

                    send_email_alert(summary_message, len(high_risk_txns))
                    st.success("✅ Summary Email Sent Successfully (all high-risk transactions included)")
                else:
                    st.info("✅ No high-risk transactions detected.")

                fraud_count = int(np.sum(predictions))
                total_txns = len(predictions)
                col1, col2, col3 = st.columns(3)
                col1.metric(label="Fraudulent Transactions", value=fraud_count)
                col2.metric(label="Total Transactions", value=total_txns)
                col3.metric(label="Fraud Ratio (%)", value=round((fraud_count/total_txns)*100, 2))

                csv = df_new.to_csv(index=False).encode('utf-8')
                st.download_button("Download Results", csv, "fraud_results.csv", "text/csv")

# --------------------------------
# MANUAL INPUT SECTION
# --------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Manual Transaction Input")

with st.form("manual_input"):
    col1, col2, col3 = st.columns(3)
    with col1:
        time = st.number_input("Time", min_value=0, value=0)
        v1 = st.number_input("V1", value=0.0)
    with col2:
        v2 = st.number_input("V2", value=0.0)
        v3 = st.number_input("V3", value=0.0)
    with col3:
        v4 = st.number_input("V4", value=0.0)
        amount = st.number_input("Transaction Amount", min_value=0.0, value=100.0)

    submitted = st.form_submit_button("Predict Fraud")

if submitted:
    sample = pd.DataFrame([[time, v1, v2, v3, v4, amount]], columns=['Time', 'V1', 'V2', 'V3', 'V4', 'Amount'])
    fraud_probability = model.predict_proba(sample)[:, 1][0]
    pred = (fraud_probability > 0.5).astype(int)

    st.markdown("<br>", unsafe_allow_html=True)
    if fraud_probability > 0.9:
        st.warning(f"High Risk Transaction Detected | Probability: {fraud_probability:.2f}")
        summary_msg = f"Manual Entry Detected as High Risk\nAmount: ₹{amount}\nRisk Score: {fraud_probability:.2f}"
        send_email_alert(summary_msg, 1)
    elif pred == 1:
        st.error(f"Fraudulent Transaction | Probability: {fraud_probability:.2f}")
    else:
        st.success(f"Legitimate Transaction | Probability: {fraud_probability:.2f}")
