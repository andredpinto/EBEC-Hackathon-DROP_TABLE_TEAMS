import numpy as np
import pandas as pd
from pathlib import PurePath


csv_path = PurePath("..","data", "metherology_dataset.csv")
df = pd.read_csv(csv_path)

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