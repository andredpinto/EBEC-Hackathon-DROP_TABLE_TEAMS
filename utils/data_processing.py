import numpy as np
import pandas as pd
from pathlib import PurePath
from math import pi, sin, cos


data_path = PurePath("..","data", "metherology_dataset.csv")
df = pd.read_csv(data_path)

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