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
targets = ['temperature_2m ', 'rain']

# Level 1
df1 = df.copy()
#df1['rain'] = df1['rain']>1
#numeric_features.append('temperature_2m ')
#preprocessor = ColumnTransformer(
#    transformers=[
#        ('num', StandardScaler(), numeric_features),
#        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value',
#                               encoded_missing_value=-1), categorical_features)
#    ])

# Level 2
X = df.drop('temperature_2m ',axis=1)
y = df['temperature_2m ']

from sklearn.ensemble import RandomForestRegressor

numeric_features.append('rain ')
preprocessor2 = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value',
                               unknown_value=-1), categorical_features)
    ]
)

pipeline2 = Pipeline(steps=[
    ('preprocessor', preprocessor2),
    ('regressor', RandomForestRegressor(n_estimators=100))
])

pipeline2.fit(X, y)
model_path = PurePath('..', 'models', 'model2.joblib')
joblib.dump(pipeline2,'../models/model2.joblib')