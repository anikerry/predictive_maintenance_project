import pandas as pd
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 1. EXTRACT: Downloading the Real Dataset ---
def fetch_and_load_data(save_raw=True):
    print("Fetching data from UCI Repository...")
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
    
    df = pd.read_csv(url)
    print("Data fetched successfully!")
    
    if save_raw:
        raw_path = os.path.join(PROJECT_ROOT, "data", "ai4i2020_raw.csv")
        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        df.to_csv(raw_path, index=False)
        print(f"Raw dataset saved to {raw_path}")
    
    return df

# --- 2. TRANSFORM: Cleaning and Engineering ---
def clean_and_transform(df):
    print("Cleaning data and engineering features...")
    
    # Drop identifiers to prevent data leakage
    df = df.drop(columns=['UDI', 'Product ID'])
    
    # One-hot encode Type column
    df = pd.get_dummies(df, columns=['Type'], drop_first=True)
    
    # Clean column names and engineer features
    df.columns = [col.replace(' ', '_').replace('[', '').replace(']', '') for col in df.columns]
    
    df['Temp_diff_K'] = df['Process_temperature_K'] - df['Air_temperature_K']
    df['Power_W'] = df['Rotational_speed_rpm'] * df['Torque_Nm']
    
    return df

# --- 3. LOAD: Saving the processed data ---
def save_data(df, filepath):
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Processed dataset saved to {filepath}")

def load_data_local(raw_data_path):
    """Load data from local file instead of URL for offline usage."""
    print(f"Loading data from local file: {raw_data_path}")
    df = pd.read_csv(raw_data_path)
    print(f"Data loaded successfully! Shape: {df.shape}")
    return df

if __name__ == "__main__":
    # Execute the pipeline
    raw_data = fetch_and_load_data(save_raw=True)  # Downloads and saves raw data locally
    processed_data = clean_and_transform(raw_data)
    
    # Save it to our data folder so the training script can use it later
    output_path = os.path.join(PROJECT_ROOT, "data", "processed_machine_data.csv")
    save_data(processed_data, output_path)
    
    print("\nPipeline Complete. Here is a preview of the clean data:")
    print(processed_data[['Air_temperature_K', 'Rotational_speed_rpm', 'Temp_diff_K', 'Power_W', 'Machine_failure']].head())