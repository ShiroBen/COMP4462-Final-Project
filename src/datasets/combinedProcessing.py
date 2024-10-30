import pandas as pd

# Load the CSV files
tracks_df = pd.read_csv('tracks_processed.csv')
spatial_data_df = pd.read_csv('spatial_data_processed.csv')

# Merge the dataframes on the respective song name columns
combined_df = pd.merge(
    spatial_data_df,
    tracks_df[['name', 'danceability', 'energy', 'key', 'loudness', 'mode', 
                'speechiness', 'acousticness', 'instrumentalness', 'liveness', 
                'valence', 'tempo', 'duration_minutes', 'time_signature', 'explicit']],
    left_on='Track Name',  # Column in spatial_data_processed.csv
    right_on='name',      # Column in tracks_processed.csv
    how='left'
)

combined_df = combined_df.drop_duplicates(subset=['Track Name', 'Date', 'Artist', 'Region'])
combined_df = combined_df.dropna()

# Save the combined dataframe to a new CSV file
combined_df.to_csv('combined_processed.csv', index=False)

print("Combined file created: combined_processed.csv")