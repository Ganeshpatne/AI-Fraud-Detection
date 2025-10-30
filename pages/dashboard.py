import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Fraud Analytics Dashboard", layout="wide", page_icon="💳")

# --- Custom Dark Theme CSS ---
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #ffffff;
    font-family: 'Poppins', sans-serif;
}
.main {
    background-color: #1c1f26;
    padding: 2rem;
    border-radius: 15px;
}
h1, h2, h3, h4, h5, h6, p, label {
    color: #ffffff !important;
}
.dataframe th {
    background-color: #2c2f36 !important;
    color: white !important;
}
.dataframe td {
    background-color: #1c1f26 !important;
    color: white !important;
}
.stMetricLabel {
    color: #cccccc !important;
}
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("Fraud Detection Analytics Dashboard")
st.markdown("Analyze transaction data to identify fraud patterns and financial risks effectively.")

# --- Load Dataset ---
try:
    df = pd.read_csv("data/creditcard.csv")
except:
    st.error("⚠️ creditcard.csv not found in the 'data' folder.")
    st.stop()

if df.empty:
    st.warning("Dataset is empty.")
    st.stop()

# --- Validate 'Class' column ---
if 'Class' not in df.columns:
    st.warning("'Class' column not found. Creating dummy data for visualization.")
    df['Class'] = 0

# --- Sidebar Filters ---
st.sidebar.header("Filter Transactions")
min_amt, max_amt = float(df['Amount'].min()), float(df['Amount'].max())
amount_range = st.sidebar.slider("Select Amount Range", min_amt, max_amt, (min_amt, max_amt))

transaction_type = st.sidebar.multiselect(
    "Select Transaction Type",
    options=['Legitimate', 'Fraudulent'],
    default=['Legitimate', 'Fraudulent']
)

df['Transaction Type'] = df['Class'].map({0: 'Legitimate', 1: 'Fraudulent'})
filtered_df = df[(df['Amount'].between(amount_range[0], amount_range[1])) &
                 (df['Transaction Type'].isin(transaction_type))]

# --- Summary Metrics ---
st.subheader("Summary Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", len(filtered_df))
col2.metric("Fraudulent Transactions", (filtered_df['Class'] == 1).sum())
col3.metric("Fraud Ratio (%)", round(((filtered_df['Class'] == 1).sum() / len(filtered_df)) * 100, 2))

# --- Fraud vs Non-Fraud Count ---
fraud_counts = filtered_df['Transaction Type'].value_counts().reset_index()
fraud_counts.columns = ['Transaction Type', 'Count']

fig1 = px.bar(
    fraud_counts,
    x='Transaction Type',
    y='Count',
    color='Transaction Type',
    title='Fraud vs Legitimate Transactions',
    color_discrete_map={'Legitimate': '#00CC96', 'Fraudulent': '#EF553B'}
)
fig1.update_layout(
    paper_bgcolor='#1c1f26',
    plot_bgcolor='#1c1f26',
    font=dict(color='white'),
    title_font=dict(size=22)
)
st.plotly_chart(fig1, use_container_width=True)

# --- Transaction Amount Distribution ---
fig2 = px.histogram(
    filtered_df,
    x='Amount',
    color='Transaction Type',
    nbins=50,
    title="Transaction Amount Distribution",
    color_discrete_map={'Legitimate': '#00CC96', 'Fraudulent': '#EF553B'}
)
fig2.update_layout(
    paper_bgcolor='#1c1f26',
    plot_bgcolor='#1c1f26',
    font=dict(color='white'),
    title_font=dict(size=22)
)
st.plotly_chart(fig2, use_container_width=True)

# --- Correlation Heatmap ---
st.subheader("Feature Correlation Heatmap")
corr = filtered_df.select_dtypes(include=['float64', 'int64']).corr()

fig3 = px.imshow(
    corr,
    color_continuous_scale='blues',
    title="Feature Correlations",
    labels=dict(color="Correlation")
)
fig3.update_layout(
    paper_bgcolor='#1c1f26',
    plot_bgcolor='#1c1f26',
    font=dict(color='white'),
    title_font=dict(size=22)
)
st.plotly_chart(fig3, use_container_width=True)

# --- Display Filtered Data ---
st.subheader("Filtered Transactions Preview")
st.dataframe(filtered_df.head(20))
