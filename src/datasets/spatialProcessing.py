import pandas as pd

# Load the CSV file
input_file = 'data.csv'
output_file = 'spatial_data_processed.csv'

country_mapping = {
    'ar': 'Argentina',
    'cl': 'Chile',
    'cr': 'Costa Rica',
    'de': 'Germany',
    'ec': 'Ecuador',
    'ee': 'Estonia',
    'fi': 'Finland',
    'fr': 'France',
    'it': 'Italy',
    'lt': 'Lithuania',
    'no': 'Norway',
    'nz': 'New Zealand',
    'ph': 'Philippines',
    'sv': 'El Salvador',
    'tr': 'Turkey',
    'tw': 'Taiwan',
    'us': 'United States',
    'hk': 'Hong Kong',
    'gr': 'Greece',
    'lv': 'Latvia',
    'au': 'Australia',
    'py': 'Paraguay',
    'global': 'Global',
    'gb': 'United Kingdom',
    'lu': 'Luxembourg',
    'do': 'Dominican Republic',
    'id': 'Indonesia',
    'sg': 'Singapore',
    'jp': 'Japan',
    'co': 'Colombia',
    'sk': 'South Korea',
    'nl': 'Netherlands',
    'ie': 'Ireland',
    'cz': 'Czech Republic',
    'at': 'Austria',
    'be': 'Belgium',
    'bo': 'Bolivia',
    'br': 'Brazil',
    'ca': 'Canada',
    'ch': 'China',
    'dk': 'Denmark',
    'es': 'Spain',
    'hn': 'Honduras',
    'hu': 'Hungary',
    'id': 'India',
    'is': 'Iceland',
    'lv': 'Latvia',
    'mx': 'Mexico',
    'my': 'Malaysia',
    'pa': 'Panama',
    'pe': 'Peru',
    'pl': 'Poland',
    'pt': 'Portugal',
    'py': 'Paraguay',
    'se': 'Sweden',
    'uy': 'Uruguay',
    'gt': 'Guatemala',
}

# Read the CSV file into a DataFrame
try:
    df = pd.read_csv(input_file)
    print(f"Successfully loaded {input_file}")
except FileNotFoundError:
    print(f"Error: {input_file} not found.")
    exit(1)

# Check if the 'streams' column exists
if 'Streams' in df.columns:
    # Assign ranks based on the 'streams' column, largest getting rank 1
    df['overall_rank'] = df['Streams'].rank(method='min', ascending=False).astype(int)
else:
    print("Warning: 'Streams' column not found in the data.")

if 'Region' in df.columns:
    df['Region'] = df['Region'].replace(country_mapping)
else:
    print("Warning: 'Region' column not found in the data.")

# Save the processed DataFrame to a new CSV file
df.to_csv(output_file, index=False)
print(f"Processed data saved to {output_file}")