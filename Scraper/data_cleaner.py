import pandas as pd
    


csv = pd.read_csv('google_maps_data.csv')
df = pd.DataFrame(csv)

df = df.drop('name', axis=1)
df = df.drop('website', axis=1)
df = df.drop('latitude', axis=1)
df = df.drop('longitude', axis=1)
df = df.drop('reviews_average', axis=1)
df = df.drop('reviews_count', axis=1)
df = df.drop('address', axis=1)
df = df[df['phone_number'].notna()]
pattern = r"\b\d{11}\b|\b\d{6} \d{5}\b"
df = df[df['phone_number'].str.contains(pattern, na=False)]

df.to_csv('filtered_data.csv', index=False)

print(df)