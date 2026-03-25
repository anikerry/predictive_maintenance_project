import pandas as pd
import os

# --- 1. EXTRACT: Downloading the Real Dataset ---
def fetch_and_load_data():
    print("Fetching data from UCI Repository...")
    # This URL points directly to the CSV file on the UCI servers
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
    
    # Pandas can read directly from a URL!
    df = pd.read_csv(url)
    print("Data fetched successfully!")
    return df

# --- 2. TRANSFORM: Cleaning and Engineering ---
def clean_and_transform(df):
    print("Cleaning data and engineering features...")
    
    # 2a. Drop irrelevant columns 
    # 'UDI' (unique ID) and 'Product ID' are just identifiers. 
    # If we leave them in, the model might try to memorize IDs instead of learning patterns.
    df = df.drop(columns=['UDI', 'Product ID'])
    
    # 2b. One-Hot Encoding
    # The 'Type' column contains letters (L, M, H for Low, Medium, High quality).
    # Machine learning models need numbers, so we convert these to binary columns.
    df = pd.get_dummies(df, columns=['Type'], drop_first=True)
    
    # 2c. Feature Engineering (Domain Knowledge)
    # Renaming columns to remove spaces and brackets for easier coding
    df.columns = [col.replace(' ', '_').replace('[', '').replace(']', '') for col in df.columns]
    
    # Create our new features to hit that "12% accuracy improvement" metric
    df['Temp_diff_K'] = df['Process_temperature_K'] - df['Air_temperature_K']
    df['Power_W'] = df['Rotational_speed_rpm'] * df['Torque_Nm']
    
    return df

# --- 3. LOAD: Saving the processed data ---
def save_data(df, filepath):
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Processed dataset saved to {filepath}")

if __name__ == "__main__":
    # Execute the pipeline
    raw_data = fetch_and_load_data()
    processed_data = clean_and_transform(raw_data)
    
    # Save it to our data folder so the training script can use it later
    save_data(processed_data, "../data/processed_machine_data.csv")
    
    print("\nPipeline Complete. Here is a preview of the clean data:")
    print(processed_data[['Air_temperature_K', 'Rotational_speed_rpm', 'Temp_diff_K', 'Power_W', 'Machine_failure']].head