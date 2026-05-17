import pandas as pd
import numpy as np
import os

def generate_high_fidelity_dataset(output_path, n_samples=10000):
    print(f"Generating high-fidelity fraud dataset with {n_samples} samples...")
    np.random.seed(42)
    
    # Kaggle structure: Time, V1-V28, Amount, Class
    # V1-V28 are PCA transformed features. We'll simulate them with normal distributions.
    # Class 0 is legit, Class 1 is fraud.
    
    fraud_rate = 0.04 # 4% fraud (results in 400 cases for 10k rows)
    n_fraud = int(n_samples * fraud_rate)
    n_legit = n_samples - n_fraud
    
    # 1. Generate Legit Data
    legit_data = {}
    legit_data['Time'] = np.random.uniform(0, 172792, n_legit)
    for i in range(1, 29):
        legit_data[f'V{i}'] = np.random.normal(0, 1, n_legit)
    legit_data['Amount'] = np.round(np.random.lognormal(mean=3, sigma=1.0, size=n_legit), 2)
    legit_data['Class'] = 0
    df_legit = pd.DataFrame(legit_data)
    
    # 2. Generate Fraud Data (distinct distribution to make it detectable)
    fraud_data = {}
    fraud_data['Time'] = np.random.uniform(0, 172792, n_fraud)
    for i in range(1, 29):
        # Shift means and scales for fraud indicators
        mean_shft = np.random.uniform(-3, 3) if i in [3, 4, 10, 12, 14, 16, 17] else 0
        scale_shft = 2.0 if i in [3, 10, 14] else 1.0
        fraud_data[f'V{i}'] = np.random.normal(mean_shft, scale_shft, n_fraud)
        
    fraud_data['Amount'] = np.round(np.random.lognormal(mean=4, sigma=1.5, size=n_fraud), 2)
    fraud_data['Class'] = 1
    df_fraud = pd.DataFrame(fraud_data)
    
    # Combine and Shuffle
    df = pd.concat([df_legit, df_fraud]).sample(frac=1).reset_index(drop=True)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully created at: {output_path}")
    print(f"Summary: {len(df)} total rows | {n_fraud} fraud cases ({fraud_rate*100}%)")

if __name__ == "__main__":
    generate_high_fidelity_dataset("data/creditcard.csv", n_samples=10000)
