import pandas as pd

# Load the CSV file
input_file = 'tracks.csv'
output_file = 'tracks_processed.csv'

# Read the CSV file into a DataFrame
try:
    df = pd.read_csv(input_file)
    print(f"Successfully loaded {input_file}")
except FileNotFoundError:
    print(f"Error: {input_file} not found.")
    exit(1)



# Check if the 'explicit' column exists
if 'explicit' in df.columns:
    # Change 0s to 'FALSE' and 1s to 'TRUE'
    df['explicit'] = df['explicit'].replace({0: 'FALSE', 1: 'TRUE'})
else:
    print("Warning: 'explicit' column not found in the data.")

if 'artists' in df.columns:
   df['artists'] = df['artists'].str.strip("[]").apply(lambda x: x.replace('"', '') if '"' in x else x.replace("'", ""))
else:
    print("Warning: 'artists' column not found in the data.")


if 'duration_ms' in df.columns:
    df['duration_minutes'] = df['duration_ms'] / 60000  # Convert milliseconds to minutes
    df.drop(columns=['duration_ms'], inplace=False)  # Optionally drop the original column
else:
    print("Warning: 'duration_ms' column not found in the data.")

if 'release_date' in df.columns:  # Replace 'date' with the actual column name if different
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_date'] = df['release_date'].dt.year  # Extract only the year
else:
    print("Warning: 'date' column not found in the data.")


df_processed = df

# Save the processed DataFrame to a new CSV file
df_processed.to_csv(output_file, index=False)
print(f"Processed data saved to {output_file}")