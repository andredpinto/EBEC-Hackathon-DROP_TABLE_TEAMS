import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from pathlib import PurePath

data_path = PurePath('..', 'data', 'meth_data_proc.csv')
df = pd.read_csv(data_path)
print(df)



# Feature types for preprocessing
# These will be encoded with sin and cos
cyclic_features = ['day_of_year', 'time_of_day']
categorical_features = ['location']
numeric_features = ['relative_humidity_2m', 'dew_point_2m ',
       'cloud_cover ', 'cloud_cover_low ', 'cloud_cover_mid ',
       'cloud_cover_highh', 'wind_speed_10m ', 'wind_direction_10m ',
       'wind_gusts_10m ', 'wind_direction_100m ', 'wind_speed_100m ',
       'pressure_msl ', 'surface_pressure ']
targets = ['temperature_2m', 'rain']


preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])
