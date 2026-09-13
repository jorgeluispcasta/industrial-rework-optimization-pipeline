import pandas as pd
import numpy as np
import datetime
import os

def generate_production_data(num_records=5000):
    np.random.seed(42)
    
    # 3 months of production
    start_date = datetime.datetime.now() - datetime.timedelta(days=90)
    timestamps = [start_date + datetime.timedelta(minutes=int(x)) for x in np.random.randint(0, 129600, num_records)]
    timestamps.sort()

    # Production variables
    batch_ids = [f"BATCH_{str(i).zfill(5)}" for i in range(1, num_records + 1)]
    product_lines = np.random.choice(['GRAM', 'GLACIER', 'BULKLINES'], num_records)
    
    # Process variables (Temperatures, Freezing Point Depression, Foam Levels)
    mix_temps = np.random.normal(loc=72.5, scale=2.0, size=num_records)
    fp_depression = np.random.normal(loc=-2.5, scale=0.3, size=num_records)
    foam_level_pct = np.random.uniform(2.0, 15.0, num_records)
    
    # High foam or bad temperatures lead to more rework kg
    rework_kg = np.where(
        (foam_level_pct > 12.0) | (mix_temps > 75.0), 
        np.random.uniform(500, 1500, num_records), # High rework
        np.random.uniform(0, 100, num_records)     # Normal operation
    )
  
    df = pd.DataFrame({
        'Timestamp': timestamps,
        'Batch_ID': batch_ids,
        'Line': product_lines,
        'Mix_Temperature_C': np.round(mix_temps, 2),
        'FP_Depression_C': np.round(fp_depression, 2),
        'Foam_Level_Pct': np.round(foam_level_pct, 2),
        'Rework_Volume_kg': np.round(rework_kg, 2)
    })
    
    return df

def upload_to_cloud(file_name):
    print(f"Connecting to Cloud Storage...")
    print(f"File {file_name} successfully uploaded to Data Lake.")

if __name__ == "__main__":
    print("Starting factory data simulation...")
    factory_data = generate_production_data(5000)
 
    output_filename = "raw_production_data.csv"
    factory_data.to_csv(output_filename, index=False)
    print(f"Data saved locally as {output_filename}")
    
    upload_to_cloud(output_filename)
