import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(
    page_title="Fraud Analytics Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# --- Enhanced Custom Dark Theme CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

body {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    color: #ffffff;
}

.main {
    background: rgba(22, 26, 35, 0.95);
    backdrop-filter: blur(10px);
    padding: 2.5rem;
    border-radius: 20px;
    animation: fadeIn 0.6s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

h1 {
    background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
    margin-bottom: 0.5rem;
    animation: slideDown 0.8s ease-out;
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-30px); }
    to { opacity: 1; transform: translateY(0); }
}

h2, h3, h4, h5, h6 {
    color: #00d4ff !important;
    font-weight: 600 !important;
    animation: fadeIn 0.8s ease-in;
}

.subtitle {
    font-size: 1.1rem;
    color: #a0aec0;
    margin-bottom: 2rem;
    font-weight: 300;
    animation: fadeIn 1s ease-in;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: rgba(15, 18, 28, 0.95);
    backdrop-filter: blur(10px);
    animation: slideInLeft 0.5s ease-out;
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #00d4ff !important;
}

/* Metric Cards */
.metric-container {
    background: rgba(30, 35, 48, 0.6);
    border: 1px solid rgba(0, 180, 216, 0.2);
    border-radius: 15px;
    padding: 1.5rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: scaleIn 0.5s ease-out;
    position: relative;
    overflow: hidden;
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}

.metric-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 180, 216, 0.1), transparent);
    transition: left 0.5s ease;
}

.metric-container:hover::before {
    left: 100%;
}

.metric-container:hover {
    border-color: rgba(0, 180, 216, 0.5);
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 180, 216, 0.2);
}

/* Dataframe Styling */
.dataframe {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(0, 180, 216, 0.2) !important;
    animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.dataframe th {
    background: linear-gradient(135deg, #1e2330 0%, #2c2f36 100%) !important;
    color: #00d4ff !important;
    font-weight: 600 !important;
    padding: 12px !important;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
}

.dataframe td {
    background-color: #1c1f26 !important;
    color: #e8e8e8 !important;
    padding: 10px !important;
    border-bottom: 1px solid rgba(0, 180, 216, 0.1) !important;
    transition: background-color 0.2s ease;
}

.dataframe tr:hover td {
    background-color: rgba(0, 180, 216, 0.05) !important;
}

/* Input Styling */
input, select {
    background-color: #1e2330 !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid rgba(0, 180, 216, 0.3) !important;
    transition: all 0.3s ease !important;
}

input:focus, select:focus {
    border-color: #00b4d8 !important;
    box-shadow: 0 0 0 3px rgba(0, 180, 216, 0.1) !important;
}

/* Chart Container */
.chart-container {
    background: rgba(30, 35, 48, 0.4);
    border: 1px solid rgba(0, 180, 216, 0.2);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeIn 0.8s ease-in;
    position: relative;
    overflow: hidden;
}

.chart-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(0, 180, 216, 0.03) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.4s ease;
}

.chart-container:hover::before {
    opacity: 1;
}

.chart-container:hover {
    border-color: rgba(0, 180, 216, 0.4);
    box-shadow: 0 8px 25px rgba(0, 180, 216, 0.15);
    transform: translateY(-2px);
}

.chart-title {
    color: #00d4ff !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    margin-bottom: 1rem !important;
    padding-left: 0.5rem;
    border-left: 3px solid #00b4d8;
}

/* Divider */
hr {
    border: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 180, 216, 0.4), transparent);
    margin: 2.5rem 0;
    animation: expandWidth 1s ease-out;
}

@keyframes expandWidth {
    from { width: 0; opacity: 0; margin-left: 50%; }
    to { width: 100%; opacity: 1; margin-left: 0; }
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    margin-top: 4rem;
    border-top: 1px solid rgba(0, 180, 216, 0.2);
    color: #a0aec0;
    font-size: 0.95rem;
    animation: fadeIn 1.5s ease-in;
}

.footer-highlight {
    background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
}

/* Button Styling */
.stButton > button {
    background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
    color: white;
    border: none;
    padding: 0.5rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(0, 180, 216, 0.2);
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 180, 216, 0.4);
}

/* Slider Styling */
[data-testid="stSlider"] {
    padding: 1rem 0;
}

[data-baseweb="slider"] {
    margin-top: 1rem;
}

/* Success/Info Messages */
.stSuccess, .stInfo, .stWarning, .stError {
    animation: slideInRight 0.5s ease-out;
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Loading Animation */
@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.loading {
    background: linear-gradient(90deg, rgba(30, 35, 48, 0.4) 0%, rgba(0, 180, 216, 0.1) 50%, rgba(30, 35, 48, 0.4) 100%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}

/* Stagger Animation for Metrics */
.metric-container:nth-child(1) { animation-delay: 0.1s; }
.metric-container:nth-child(2) { animation-delay: 0.2s; }
.metric-container:nth-child(3) { animation-delay: 0.3s; }
.metric-container:nth-child(4) { animation-delay: 0.4s; }

/* Chart Container Stagger */
.chart-container:nth-of-type(1) { animation-delay: 0.2s; }
.chart-container:nth-of-type(2) { animation-delay: 0.3s; }
.chart-container:nth-of-type(3) { animation-delay: 0.4s; }
.chart-container:nth-of-type(4) { animation-delay: 0.5s; }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

# --- Title ---
st.title("Fraud Analytics Dashboard")
st.markdown("<p class='subtitle'>Comprehensive insights and visualization of transaction patterns and fraud detection metrics</p>", unsafe_allow_html=True)

# Add navigation button to upload page
col1, col2, col3 = st.columns([1, 8, 1])
with col3:
    if st.button("Upload New Data"):
        st.switch_page("app.py")

st.markdown("<hr>", unsafe_allow_html=True)

# --- Load Dataset ---
df = None

# Try to load from session state first
if st.session_state.uploaded_data is not None:
    df = st.session_state.uploaded_data
    st.success("Using uploaded data from session")
else:
    # Fallback to file system
    try:
        df = pd.read_csv("data/creditcard.csv")
        st.info("Loaded data from file system (data/creditcard.csv)")
    except:
        st.error("No data found! Please upload a CSV file first.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Upload Page", use_container_width=True):
                st.switch_page("app.py")
        
        st.stop()

if df is None or df.empty:
    st.warning("Dataset is empty. Please check your data source.")
    st.stop()

# --- Validate 'Class' column ---
if 'Class' not in df.columns:
    st.warning("'Class' column not found. Creating sample data for visualization purposes.")
    df['Class'] = 0

# --- Sidebar Filters ---
st.sidebar.markdown("### Filter Controls")
st.sidebar.markdown("---")

min_amt, max_amt = float(df['Amount'].min()), float(df['Amount'].max())
amount_range = st.sidebar.slider(
    "Transaction Amount Range",
    min_amt,
    max_amt,
    (min_amt, max_amt),
    help="Filter transactions by amount"
)

transaction_type = st.sidebar.multiselect(
    "Transaction Type",
    options=['Legitimate', 'Fraudulent'],
    default=['Legitimate', 'Fraudulent'],
    help="Select transaction types to display"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")

# Map transaction types
df['Transaction Type'] = df['Class'].map({0: 'Legitimate', 1: 'Fraudulent'})

# Apply filters
filtered_df = df[
    (df['Amount'].between(amount_range[0], amount_range[1])) &
    (df['Transaction Type'].isin(transaction_type))
]

# Sidebar stats
total_filtered = len(filtered_df)
fraud_filtered = (filtered_df['Class'] == 1).sum()
st.sidebar.metric("Filtered Transactions", f"{total_filtered:,}")
st.sidebar.metric("Fraudulent", f"{fraud_filtered:,}")
st.sidebar.metric("Legitimate", f"{total_filtered - fraud_filtered:,}")

# --- Summary Metrics ---
st.markdown("### Key Performance Indicators")

# Create custom styled metrics using columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metric-container'>
        <div style='color: #a0aec0; font-size: 0.95rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;'>
            TOTAL TRANSACTIONS
        </div>
        <div style='background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 2.2rem;'>
            {len(filtered_df):,}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    fraud_count = (filtered_df['Class'] == 1).sum()
    st.markdown(f"""
    <div class='metric-container'>
        <div style='color: #a0aec0; font-size: 0.95rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;'>
            FRAUDULENT
        </div>
        <div style='background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 2.2rem;'>
            {fraud_count:,}
        </div>
        <div style='color: #EF553B; font-size: 0.9rem; margin-top: 0.5rem;'>
            ↓ {fraud_count}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    legit_count = (filtered_df['Class'] == 0).sum()
    st.markdown(f"""
    <div class='metric-container'>
        <div style='color: #a0aec0; font-size: 0.95rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;'>
            LEGITIMATE
        </div>
        <div style='background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 2.2rem;'>
            {legit_count:,}
        </div>
        <div style='color: #00CC96; font-size: 0.9rem; margin-top: 0.5rem;'>
            ↑ {legit_count}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    fraud_ratio = ((filtered_df['Class'] == 1).sum() / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.markdown(f"""
    <div class='metric-container'>
        <div style='color: #a0aec0; font-size: 0.95rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;'>
            FRAUD RATE
        </div>
        <div style='background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 2.2rem;'>
            {fraud_ratio:.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Row 1: Fraud Distribution ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='chart-container'>
        <div class='chart-title'>Transaction Distribution</div>
    """, unsafe_allow_html=True)
    
    fraud_counts = filtered_df['Transaction Type'].value_counts().reset_index()
    fraud_counts.columns = ['Transaction Type', 'Count']
    
    fig1 = px.pie(
        fraud_counts,
        values='Count',
        names='Transaction Type',
        color='Transaction Type',
        color_discrete_map={'Legitimate': '#00CC96', 'Fraudulent': '#EF553B'},
        hole=0.4
    )
    fig1.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=14,
        marker=dict(line=dict(color='#0a0e27', width=2))
    )
    fig1.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='chart-container'>
        <div class='chart-title'>Transaction Count by Type</div>
    """, unsafe_allow_html=True)
    
    fig2 = px.bar(
        fraud_counts,
        x='Transaction Type',
        y='Count',
        color='Transaction Type',
        color_discrete_map={'Legitimate': '#00CC96', 'Fraudulent': '#EF553B'},
        text='Count'
    )
    fig2.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        textfont_size=14
    )
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        xaxis=dict(title='', gridcolor='rgba(0, 180, 216, 0.1)'),
        yaxis=dict(title='Count', gridcolor='rgba(0, 180, 216, 0.1)'),
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Row 2: Amount Analysis ---
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='chart-container'>
        <div class='chart-title'>Transaction Amount Distribution</div>
    """, unsafe_allow_html=True)
    
    fig3 = px.histogram(
        filtered_df,
        x='Amount',
        color='Transaction Type',
        nbins=50,
        color_discrete_map={'Legitimate': '#00CC96', 'Fraudulent': '#EF553B'},
        barmode='overlay',
        opacity=0.7
    )
    fig3.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        xaxis=dict(title='Transaction Amount', gridcolor='rgba(0, 180, 216, 0.1)'),
        yaxis=dict(title='Frequency', gridcolor='rgba(0, 180, 216, 0.1)'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='chart-container'>
        <div class='chart-title'>Amount Comparison Box Plot</div>
    """, unsafe_allow_html=True)
    
    fig4 = px.box(
        filtered_df,
        x='Transaction Type',
        y='Amount',
        color='Transaction Type',
        color_discrete_map={'Legitimate': '#00CC96', 'Fraudulent': '#EF553B'},
        points='outliers'
    )
    fig4.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        xaxis=dict(title='', gridcolor='rgba(0, 180, 216, 0.1)'),
        yaxis=dict(title='Amount', gridcolor='rgba(0, 180, 216, 0.1)'),
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Correlation Heatmap (if enough numeric columns) ---
st.markdown("<br>", unsafe_allow_html=True)
numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns
if len(numeric_cols) > 3:
    st.markdown("""
    <div class='chart-container'>
        <div class='chart-title'>Feature Correlation Matrix</div>
    """, unsafe_allow_html=True)
    
    # Limit to first 15 columns for better visualization
    cols_to_show = list(numeric_cols[:15])
    corr = filtered_df[cols_to_show].corr()
    
    fig5 = px.imshow(
        corr,
        color_continuous_scale='RdBu_r',
        aspect='auto',
        labels=dict(color="Correlation"),
        zmin=-1,
        zmax=1
    )
    fig5.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=10),
        height=600,
        xaxis=dict(tickangle=-45),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Data Table ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Transaction Data Explorer")

# Add search/filter option
search_col1, search_col2 = st.columns([3, 1])
with search_col1:
    show_count = st.slider("Number of rows to display", 10, 100, 20, 10)
with search_col2:
    show_fraud_only = st.checkbox("Show Fraudulent Only", value=False)

display_df = filtered_df[filtered_df['Class'] == 1] if show_fraud_only else filtered_df

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.dataframe(
    display_df.head(show_count),
    use_container_width=True,
    height=400
)
st.markdown("</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class='footer'>
    <p>Developed by <span class='footer-highlight'>Ganesh Patne</span>, <span class='footer-highlight'>Sujal Surve</span> and <span class='footer-highlight'>Aditya Tambadkar</span></p>
    <p style='font-size: 0.85rem; color: #718096; margin-top: 0.5rem;'>Advanced Analytics | Real-time Insights | AI-Powered Detection</p>
</div>
""", unsafe_allow_html=True)