import pandas as pd

def main():
    # Read existing filtered data if it exists
    try:
        existing_data = pd.read_csv('filtered_data.csv')
    except FileNotFoundError:
        existing_data = pd.DataFrame()

    # Read new data
    csv = pd.read_csv('google_maps_data.csv')
    df = pd.DataFrame(csv)

    # Perform filtering operations
    df = df.drop(['name', 'website', 'latitude', 'longitude', 'reviews_average', 'reviews_count', 'address'], axis=1)
    df = df[df['phone_number'].notna()]
    pattern = r"\b\d{11}\b|\b\d{6} \d{5}\b"
    df = df[df['phone_number'].str.contains(pattern, na=False)]

    # Combine existing data with new filtered data
    df_combined = pd.concat([existing_data, df], ignore_index=True)

    # Save the combined data to the CSV file
    df_combined.to_csv('filtered_data.csv', index=False)

    print(df_combined)

if __name__ == "__main__":
    main()
