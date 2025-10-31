import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(
    page_title="Fraud Detection - Upload",
    layout="wide",
    page_icon="📤",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
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

.subtitle {
    font-size: 1.1rem;
    color: #a0aec0;
    margin-bottom: 2rem;
    font-weight: 300;
    animation: fadeIn 1s ease-in;
}

/* Upload Section Styling */
.upload-container {
    background: rgba(30, 35, 48, 0.6);
    border: 2px dashed rgba(0, 180, 216, 0.3);
    border-radius: 15px;
    padding: 3rem;
    margin: 2rem 0;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: scaleIn 0.6s ease-out;
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

.upload-container:hover {
    border-color: rgba(0, 180, 216, 0.6);
    background: rgba(30, 35, 48, 0.8);
    transform: translateY(-2px);
    box-shadow: 0 10px 40px rgba(0, 180, 216, 0.15);
}

/* File Uploader Custom Styling */
[data-testid="stFileUploader"] {
    background: transparent !important;
}

[data-testid="stFileUploader"] > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

[data-testid="stFileUploader"] section {
    background: rgba(20, 25, 35, 0.8) !important;
    border: 2px dashed rgba(0, 180, 216, 0.4) !important;
    border-radius: 12px !important;
    padding: 2.5rem !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"] section:hover {
    border-color: rgba(0, 180, 216, 0.7) !important;
    background: rgba(25, 30, 40, 0.9) !important;
}

[data-testid="stFileUploader"] section > div {
    text-align: center !important;
}

[data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    margin-top: 1rem !important;
}

[data-testid="stFileUploader"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 180, 216, 0.3) !important;
}

/* Success/Info Box Styling */
.success-box {
    background: rgba(0, 204, 150, 0.1);
    border: 1px solid rgba(0, 204, 150, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

.info-box {
    background: rgba(0, 180, 216, 0.1);
    border: 1px solid rgba(0, 180, 216, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    animation: slideIn 0.5s ease-out;
}

/* Metric Cards */
.metric-card {
    background: rgba(30, 35, 48, 0.6);
    border: 1px solid rgba(0, 180, 216, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.metric-card:hover {
    border-color: rgba(0, 180, 216, 0.5);
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 180, 216, 0.2);
}

.metric-label {
    color: #a0aec0;
    font-size: 0.9rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

.metric-value {
    background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 2rem;
}

/* Requirements Section */
.requirements-box {
    background: rgba(30, 35, 48, 0.5);
    border: 1px solid rgba(0, 180, 216, 0.2);
    border-radius: 12px;
    padding: 2rem;
    margin: 2rem 0;
    animation: fadeIn 0.8s ease-in;
}

.requirements-box h3 {
    color: #00d4ff !important;
    font-weight: 600 !important;
    margin-bottom: 1rem !important;
}

.requirements-box ul {
    color: #e8e8e8;
    line-height: 1.8;
    padding-left: 1.5rem;
}

.requirements-box li {
    margin-bottom: 0.5rem;
}

.requirements-box strong {
    color: #00d4ff;
}

/* Button Styling */
.stButton > button {
    background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    width: 100%;
    box-shadow: 0 4px 15px rgba(0, 180, 216, 0.2);
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 180, 216, 0.4);
}

/* Dataframe Styling */
.dataframe {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(0, 180, 216, 0.2) !important;
    animation: fadeIn 0.8s ease-in;
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
}

.dataframe tr:hover td {
    background-color: rgba(0, 180, 216, 0.05) !important;
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
    from { width: 0; opacity: 0; }
    to { width: 100%; opacity: 1; }
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
    font-weight: 600;
}

/* Section Headers */
h2, h3 {
    color: #00d4ff !important;
    font-weight: 600 !important;
    animation: fadeIn 0.8s ease-in;
}

/* Pulse Animation for Important Elements */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.pulse {
    animation: pulse 2s infinite;
}
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

# --- Title ---
st.title("Fraud Detection Data Upload")
st.markdown("<p class='subtitle'>Upload your credit card transaction data for comprehensive fraud analysis</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)



uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=['csv'],
    help="Upload your creditcard.csv file containing transaction data",
    label_visibility="collapsed"
)

st.markdown("</div>", unsafe_allow_html=True)

# --- Process Uploaded File ---
if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Store in session state
        st.session_state.uploaded_data = df
        
        # Display success message
        
        st.success(f"File uploaded successfully! Loaded {len(df):,} transactions")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Show data preview
        st.markdown("### Data Preview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total Rows</div>
                <div class='metric-value'>{len(df):,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total Columns</div>
                <div class='metric-value'>{len(df.columns)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if 'Class' in df.columns:
                fraud_count = (df['Class'] == 1).sum()
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Fraudulent</div>
                    <div class='metric-value'>{fraud_count:,}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='metric-card'>
                    <div class='metric-label'>Fraudulent</div>
                    <div class='metric-value'>N/A</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if 'Class' in df.columns:
                legit_count = (df['Class'] == 0).sum()
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Legitimate</div>
                    <div class='metric-value'>{legit_count:,}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='metric-card'>
                    <div class='metric-label'>Legitimate</div>
                    <div class='metric-value'>N/A</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display first few rows
        st.dataframe(df.head(10), use_container_width=True, height=300)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation button to dashboard
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Dashboard", use_container_width=True):
                st.switch_page("C:\\Users\\ganes\\OneDrive\\Desktop\\AI fraud detection\\pages\\dashboard.py")
        
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        st.info("Please ensure your CSV file is properly formatted with a 'Class' column for fraud labels.")

else:
    # Show instructions when no file is uploaded

    st.info("Please upload a CSV file to begin analysis")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Requirements Section
    st.markdown("""
    <div class='requirements-box'>
        <h3>Required Data Format</h3>
        <p style='color: #a0aec0; margin-bottom: 1rem;'>Your CSV file should contain:</p>
        <ul>
            <li><strong>Class:</strong> Binary column (0 = Legitimate, 1 = Fraudulent)</li>
            <li><strong>Amount:</strong> Transaction amount</li>
            <li><strong>Time:</strong> Time of transaction (optional)</li>
            <li><strong>V1-V28:</strong> PCA transformed features (optional)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if data exists in session state
    if st.session_state.uploaded_data is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.info("Data is already loaded in session. You can go directly to the dashboard!")
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Dashboard", use_container_width=True):
                st.switch_page("C:\\Users\\ganes\\OneDrive\\Desktop\\AI fraud detection\\pages\\dashboard.py")

# --- Footer ---
st.markdown("""
<div class='footer'>
    <p>Developed by <span class='footer-highlight'>Ganesh Patne</span>, <span class='footer-highlight'>Sujal Surve</span> and <span class='footer-highlight'>Aditya Tambadkar</span></p>
    <p style='font-size: 0.85rem; color: #718096; margin-top: 0.5rem;'>Advanced Analytics | Real-time Insights | AI-Powered Detection</p>
</div>
""", unsafe_allow_html=True)