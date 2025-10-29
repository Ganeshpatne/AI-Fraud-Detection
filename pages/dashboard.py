import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fraud Analytics Dashboard", layout="wide", page_icon="📊")

st.title("📊 Fraud Detection Dashboard")

st.write("Visualize and analyze transaction patterns to detect potential frauds.")

try:
    df = pd.read_csv("data/creditcard.csv")
except:
    st.error("⚠️ creditcard.csv not found in data folder.")
    st.stop()

if df.empty:
    st.warning("Dataset is empty.")
    st.stop()

# --- Check for 'Class' column ---
if 'Class' not in df.columns:
    st.warning("No 'Class' column found, creating dummy data for visualization.")
    df['Class'] = 0

# --- Fraud vs Non-Fraud Count ---
fraud_counts = df['Class'].value_counts().reset_index()
fraud_counts.columns = ['Class', 'Count']

fig1 = px.bar(fraud_counts, x='Class', y='Count',
              color='Class', title='Fraud vs Non-Fraud Transactions',
              labels={'Class': 'Transaction Type'})
st.plotly_chart(fig1, use_container_width=True)

# --- Transaction Amount Distribution ---
fig2 = px.histogram(df, x='Amount', color='Class', nbins=50,
                    title="Transaction Amount Distribution")
st.plotly_chart(fig2, use_container_width=True)

# --- Correlation Heatmap ---
st.subheader("🔍 Correlation Heatmap")
corr = df.select_dtypes(include=['float64', 'int64']).corr()
fig3 = px.imshow(corr, color_continuous_scale='viridis', title="Feature Correlations")
st.plotly_chart(fig3, use_container_width=True)
