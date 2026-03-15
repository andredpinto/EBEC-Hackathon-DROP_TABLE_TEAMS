import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from pathlib import PurePath

seed = 42   # use this variable for random state

data_path = PurePath('..', 'data', 'meth_data_proc.csv')
df = pd.read_csv(data_path)

# Feature types for preprocessing
# These will be encoded with sin and cos
categorical_features = ['location']
numeric_features = ['relative_humidity_2m', 'dew_point_2m ',
       'cloud_cover ', 'cloud_cover_low ', 'cloud_cover_mid ',
       'cloud_cover_highh', 'wind_speed_10m ', 'wind_direction_10m ',
       'wind_gusts_10m ', 'wind_direction_100m ', 'wind_speed_100m ',
       'pressure_msl ', 'surface_pressure ']
targets = ['temperature_2m ', 'rain ']  # Just to remember the names

# Level 1
from sklearn.ensemble import RandomForestClassifier

df1 = df.copy()
df1['rain '] = (df1['rain ']>0).astype(bool)

# Undersampling
# Separate majority and minority classes
df_majority = df1[df1['rain '] == False]
df_minority = df1[df1['rain '] == True]

# Undersample majority class
df_majority_undersampled = df_majority.sample(n=len(df_minority), random_state=42)

# Concatenate minority class with undersampled majority class
df1 = pd.concat([df_majority_undersampled, df_minority])

X1 = df1.drop(['rain ', 'location'], axis=1)    # Dropped location during testing, so we do it here too
y1 = df1['rain ']

numeric_features1 = numeric_features + ['temperature_2m ']
preprocessor1 = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features1),
#        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value',
#                               unknown_value=-1), categorical_features)
    ])

pipeline1 = Pipeline(steps=[
    ('preprocessor', preprocessor1),
    ('classifier', RandomForestClassifier(random_state=seed))
])

# Level 2
X2 = df.drop('temperature_2m ',axis=1)
y2 = df['temperature_2m ']

numeric_features.append('rain ')
preprocessor2 = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value',
                               unknown_value=-1), categorical_features)
    ]
)

from xgboost import XGBRegressor
model2 = XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state = seed)

pipeline2 = Pipeline(steps=[
    ('preprocessor', preprocessor2),
    ('regressor', model2)
])

# Level 3
prediction_columns = ['temperature_2m ', 'relative_humidity_2m', 'dew_point_2m ', 'pressure_msl ']
df3 = df[prediction_columns].copy()

preprocessor3 = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), prediction_columns),
    ])

import hdbscan

hdbscan_clustering = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=5, metric='euclidean')

pipeline3 = Pipeline(steps=[
    ('preprocessor', preprocessor3),
    ('clusterer', hdbscan_clustering)
])

#print('Training model 3')
#clusters = pipeline3.fit_predict(df3)
#
#df3['cluster_labels_hdbscan'] = clusters
## Selecionar os clusters com anomalias
#
#t = df3.groupby('cluster_labels_hdbscan')[['temperature_2m ', "relative_humidity_2m","dew_point_2m "]].mean()
#
## Filter for clusters where mean temperature is below 0
##filtered_t = t[t['temperature_2m '] < 0.15]
#filtered_t = t[t['dew_point_2m '] < 0.1][t["temperature_2m "]<0.2]


#print("Mean of 'temperature_2m ', 'rain' and 'dew_point_2m' for clusters with mean temperature below 0:")
#print(filtered_t)

# Level 4
accidents_path = PurePath('..', 'data', 'accidents_dataset.csv')
accid_df = pd.read_csv(accidents_path)
og_data_path = PurePath('..', 'data', 'metherology_dataset.csv')
og_df = pd.read_csv(og_data_path)

og_df['time'] = pd.to_datetime(og_df['time'])
og_df['merge_date'] = og_df['time'].dt.date
accid_df['time'] = pd.to_datetime(accid_df['time'])
accid_df['merge_date'] = accid_df['time'].dt.date
# Merge df_temp_weather and df_temp_accidents to get hourly weather with daily accident counts
# This temporary merged_df_hourly will serve as the source for aggregation.
merged_df_hourly = pd.merge(
    og_df,
    accid_df[['location', 'merge_date', 'accidents']],
    on=['location', 'merge_date'],
    how='left'
)

# Drop the temporary 'merge_date' column from the hourly merged_df if not needed for aggregation key
# For daily aggregation, we will use 'time'.dt.date
merged_df_hourly = merged_df_hourly.drop(columns=['merge_date'])

# Ensure 'time' is datetime (it should be from previous step)
merged_df_hourly['time'] = pd.to_datetime(merged_df_hourly['time'])

# Create a daily date key for grouping
merged_df_hourly['daily_date'] = merged_df_hourly['time'].dt.date

# Define aggregation functions for numerical columns
# For weather features, taking the mean for continuous values.
# For 'rain ', which is boolean, sum gives total hours it rained.
# For 'accidents', it's already a daily value, so mean is appropriate (it should be constant per day).

aggregation_dict = {}
for col in merged_df_hourly.columns:
    if col not in ['location', 'time', 'daily_date']:
        if merged_df_hourly[col].dtype == 'bool':
            aggregation_dict[col] = lambda x: x.sum().astype(int) # Count rainy hours
        elif pd.api.types.is_numeric_dtype(merged_df_hourly[col]):
            aggregation_dict[col] = 'mean'

# Group by location and the daily date, then aggregate
df4 = merged_df_hourly.groupby(['location', 'daily_date']).agg(aggregation_dict).reset_index()
df4 = df4.dropna(subset=['accidents'])

# Rename 'daily_date' to 'date' for clarity if preferred
df4 = df4.rename(columns={'daily_date': 'date'})

df4 = pd.get_dummies(df4, columns=['location'], drop_first=True, dtype=int)

df4 = df4.drop('date', axis=1)

X4 = df4.drop('accidents', axis=1)
y4 = df4['accidents']

model4 = XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=seed)

# Training and saving models

print("Training model 1...")
pipeline1.fit(X1, y1)
joblib.dump(pipeline1,'../models/model1.joblib')

print("Training model 2...")
pipeline2.fit(X2, y2)
joblib.dump(pipeline2,'../models/model2.joblib')

print("Saving model 3...")
joblib.dump(pipeline3,'../models/model3.joblib')

print("Training model 4..")
model4.fit(X4, y4)
joblib.dump(model4, '../models/model4.joblib')
print('Done')