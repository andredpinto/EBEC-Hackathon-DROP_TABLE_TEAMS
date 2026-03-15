import numpy as np
import pandas as pd
from pathlib import PurePath
from math import pi, sin, cos


data_path = PurePath("..","data", "metherology_dataset.csv")
df = pd.read_csv(data_path)

# Remove duplicate rows
df = df.drop_duplicates()

# Define key meteorological columns to check for data quality
cols_to_check = ['temperature_2m', 'dew_point_2m', 'cloud_cover', 'wind_speed_10m', 'pressure_msl']
cols_to_fix = [col for col in cols_to_check if col in df.columns]

# Handle missing values
# If nulls are found, impute them using the column mean
if df[cols_to_fix].isnull().sum().sum() > 0:
    df[cols_to_fix] = df[cols_to_fix].fillna(df[cols_to_fix].mean())

# Converting time (date) to correct format
df['time'] = pd.to_datetime(df['time'])

# For now adding just day_of_year and time_of_day
# In the future these should be encoded with sin and cos
# sin/cos(2pi(value/max(value)))
df['day_of_year'] = df['time'].dt.day_of_year
df['time_of_day'] = df['time'].dt.hour + df['time'].dt.minute / 60
# Our dataset has no minutes other than 0 (I think) but this handles them if they exist
# It also completely ignores seconds and the year
df = df.drop('time', axis=1)

# Cyclical encoding
# This maps hour and day to a trigonometric circle (it separates them in two variables)
df['day_sin'] = [sin(2*pi*(v / 365)) for v in df['day_of_year']]
df['day_cos'] = [cos(2*pi*(v / 365)) for v in df['day_of_year']]
df['hour_sin'] = [sin(2*pi*(v / 24)) for v in df['time_of_day']]
df['hour_cos'] = [cos(2*pi*(v / 24)) for v in df['time_of_day']]
# There is probably a much more efficient way to do this
df = df.drop(['day_of_year', 'time_of_day'], axis=1)

print(df[['day_sin', 'day_cos', 'hour_sin', 'hour_cos']].describe())

# Saving processed file
save_name = 'meth_data_proc.csv'
save_path = PurePath('..', 'data', save_name)
df.to_csv(save_path, index=False)
