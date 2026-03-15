import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from pathlib import PurePath

seed = 42   # use this variable for random state

data_path = PurePath('..', 'data', 'meth_data_proc.csv')
df = pd.read_csv(data_path)
print(df)

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


# Training and saving models

print("Training model 1...")
pipeline1.fit(X1, y1)
joblib.dump(pipeline1,'../models/model1.joblib')

print("Training model 2...")
pipeline2.fit(X2, y2)
joblib.dump(pipeline2,'../models/model2.joblib')

print('Done')