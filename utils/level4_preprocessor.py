import sys
import pandas as pd
from pathlib import PurePath

file_path = sys.argv[1]

df = pd.read_csv(file_path)
df['time'] = pd.to_datetime(df['time'])
df['merge_date'] = df['time'].dt.date
df = df.drop(columns=['merge_date'])
df['time'] = pd.to_datetime(df['time'])
df['daily_date'] = df['time'].dt.date
aggregation_dict = {}
for col in df.columns:
    if col not in ['location', 'time', 'daily_date']:
        if df[col].dtype == 'bool':
            aggregation_dict[col] = lambda x: x.sum().astype(int) # Count rainy hours
        elif pd.api.types.is_numeric_dtype(df[col]):
            aggregation_dict[col] = 'mean'

# Group by location and the daily date, then aggregate
df = df.groupby(['location', 'daily_date']).agg(aggregation_dict).reset_index()
df = df.dropna(subset=['accidents'])

# Rename 'daily_date' to 'date' for clarity if preferred
df = df.rename(columns={'daily_date': 'date'})

df = pd.get_dummies(df, columns=['location'], drop_first=True, dtype=int)

df = df.drop('date', axis=1)

save_path = PurePath('..', 'data', 'level4_processed.csv')
df.to_csv(save_path)