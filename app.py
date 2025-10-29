import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import os

st.set_page_config(page_title="AI Fraud Detection System", layout="wide", page_icon="💳")

# --- Custom Dark Theme CSS ---
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
    font-family: 'Poppins', sans-serif;
}
.main {
    background-color: #1c1f26;
    padding: 2rem;
    border-radius: 15px;
}
.stButton>button {
    background-color: #0066cc;
    color: white;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    border: none;
}
.stButton>button:hover {
    background-color: #004d99;
}
</style>
""", unsafe_allow_html=True)

st.title("💳 AI-Powered Fraud Detection System")
st.write("Detect fraudulent transactions in real-time using machine learning.")

# --- Load or Train Model ---
@st.cache_resource
def load_or_train_model():
    os.makedirs("model", exist_ok=True)
    try:
        model = joblib.load("model/fraud_model.pkl")
        return model
    except:
        df = pd.read_csv("data/creditcard.csv")

        if df.empty:
            st.error("🚫 Dataset is empty. Please check data/creditcard.csv.")
            return None

        df = df.select_dtypes(include=[np.number])

        if 'Class' not in df.columns:
            st.warning("⚠️ 'Class' column missing. Creating dummy labels.")
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

# --- File Upload Section ---
st.subheader("📂 Upload Transactions CSV")
uploaded_file = st.file_uploader("Upload a CSV file to analyze transactions", type=["csv"])

if uploaded_file is not None:
    df_new = pd.read_csv(uploaded_file)

    if df_new.empty:
        st.error("Uploaded file is empty.")
    else:
        st.write("📊 Preview of Uploaded Data:")
        st.dataframe(df_new.head())

        if st.button("🔍 Predict Fraudulent Transactions"):
            X_new = df_new.select_dtypes(include=[np.number])
            X_new = X_new.drop('Class', axis=1, errors='ignore')

            if X_new.empty:
                st.error("No numeric columns found for prediction.")
            else:
                predictions = model.predict(X_new)
                df_new['Fraud_Prediction'] = predictions
                st.success("✅ Prediction Complete")

                st.dataframe(df_new.head(10))

                fraud_count = int(np.sum(predictions))
                total_txns = len(predictions)
                st.metric(label="Fraudulent Transactions", value=fraud_count)
                st.metric(label="Total Transactions", value=total_txns)
                st.metric(label="Fraud Ratio (%)", value=round((fraud_count/total_txns)*100, 2))

                csv = df_new.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Results", csv, "fraud_results.csv", "text/csv")

# --- Manual Input ---
st.subheader("🧮 Try Manual Transaction Input")

with st.form("manual_input"):
    time = st.number_input("Time", min_value=0, value=0)
    v1 = st.number_input("V1", value=0.0)
    v2 = st.number_input("V2", value=0.0)
    v3 = st.number_input("V3", value=0.0)
    v4 = st.number_input("V4", value=0.0)
    amount = st.number_input("Transaction Amount", min_value=0.0, value=100.0)
    submitted = st.form_submit_button("Predict Fraud")

if submitted:
    sample = pd.DataFrame([[time, v1, v2, v3, v4, amount]],
                          columns=['Time', 'V1', 'V2', 'V3', 'V4', 'Amount'])
    pred = model.predict(sample)[0]
    if pred == 1:
        st.error("⚠️ Fraudulent Transaction Detected!")
    else:
        st.success("✅ Legitimate Transaction")
