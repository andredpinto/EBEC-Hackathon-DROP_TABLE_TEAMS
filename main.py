from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel
import joblib
import pandas as pd
import os
import uuid
from utils.data_processing import pre_process

app = FastAPI(title="Weather Prediction API")
templates = Jinja2Templates(directory="templates")

pipeline1 = joblib.load('models/model1.joblib')
pipeline2 = joblib.load('models/model2.joblib')
model4 = joblib.load('models/model4.joblib')
model51 = joblib.load('models/model51.joblib')
model52 = joblib.load('models/model52.joblib')
model53 = joblib.load('models/model53.joblib')

class RainPredictionData(BaseModel):
    relative_humidity_2m: float
    dew_point_2m: float
    cloud_cover: float
    cloud_cover_low: float
    cloud_cover_mid: float
    cloud_cover_highh: float
    wind_speed_10m: float
    wind_direction_10m: float
    wind_gusts_10m: float
    wind_direction_100m: float
    wind_speed_100m: float
    pressure_msl: float
    surface_pressure: float
    temperature_2m: float

class TemperaturePredictionData(BaseModel):
    relative_humidity_2m: float
    dew_point_2m: float
    cloud_cover: float
    cloud_cover_low: float
    cloud_cover_mid: float
    cloud_cover_highh: float
    wind_speed_10m: float
    wind_direction_10m: float
    wind_gusts_10m: float
    wind_direction_100m: float
    wind_speed_100m: float
    pressure_msl: float
    surface_pressure: float
    rain: float
    day_sin: float
    day_cos: float
    hour_sin: float
    hour_cos: float
    location: str = "Aveiro"


@app.post("/rain/predict")
async def predict_rain(data: RainPredictionData):
    try:
        input_data = pd.DataFrame({
            'relative_humidity_2m': [data.relative_humidity_2m],
            'dew_point_2m ': [data.dew_point_2m],
            'cloud_cover ': [data.cloud_cover],
            'cloud_cover_low ': [data.cloud_cover_low],
            'cloud_cover_mid ': [data.cloud_cover_mid],
            'cloud_cover_highh': [data.cloud_cover_highh],
            'wind_speed_10m ': [data.wind_speed_10m],
            'wind_direction_10m ': [data.wind_direction_10m],
            'wind_gusts_10m ': [data.wind_gusts_10m],
            'wind_direction_100m ': [data.wind_direction_100m],
            'wind_speed_100m ': [data.wind_speed_100m],
            'pressure_msl ': [data.pressure_msl],
            'surface_pressure ': [data.surface_pressure],
            'temperature_2m ': [data.temperature_2m]
        })

        prediction = pipeline1.predict(input_data)[0]

        return {
            "rain_prediction": bool(prediction),
            "rain_status": "Raining" if prediction else "Not Raining"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/temperature/predict")
async def predict_temperature(data: TemperaturePredictionData):
    try:
        input_data = pd.DataFrame({
            'relative_humidity_2m': [data.relative_humidity_2m],
            'dew_point_2m ': [data.dew_point_2m],
            'cloud_cover ': [data.cloud_cover],
            'cloud_cover_low ': [data.cloud_cover_low],
            'cloud_cover_mid ': [data.cloud_cover_mid],
            'cloud_cover_highh': [data.cloud_cover_highh],
            'wind_speed_10m ': [data.wind_speed_10m],
            'wind_direction_10m ': [data.wind_direction_10m],
            'wind_gusts_10m ': [data.wind_gusts_10m],
            'wind_direction_100m ': [data.wind_direction_100m],
            'wind_speed_100m ': [data.wind_speed_100m],
            'pressure_msl ': [data.pressure_msl],
            'surface_pressure ': [data.surface_pressure],
            'rain ': [data.rain],
            'day_sin': [data.day_sin],
            'day_cos': [data.day_cos],
            'hour_sin': [data.hour_sin],
            'hour_cos': [data.hour_cos],
            'location': [data.location]
        })

        prediction = pipeline2.predict(input_data)[0]

        return {
            "temperature_prediction": float(prediction),
            "temperature_celsius": round(float(prediction), 2),
            "temperature_fahrenheit": round(float(prediction) * 9/5 + 32, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return FileResponse('static/index.html')

@app.get("/rain")
async def rain_interface():
    return FileResponse('static/rain.html')

@app.post("/rain/upload")
async def upload_rain_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        unique_filename = str(uuid.uuid4()) + '_' + file.filename
        raw_filepath = os.path.join('uploads', unique_filename)
        
        os.makedirs('uploads', exist_ok=True)
        with open(raw_filepath, 'wb') as f:
            f.write(contents)
        
        processed_filename = 'proc_' + unique_filename
        processed_filepath = os.path.join('uploads', processed_filename)
        
        pre_process(raw_filepath, processed_filepath)
        
        return {"filename": processed_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rain/download/{filename}")
async def download_results(filename: str):
    try:
        filepath = os.path.join('uploads', filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=filepath,
            filename=f"rain_predictions_{filename}",
            media_type='text/csv'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/temperature/upload")
async def upload_temperature_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        unique_filename = str(uuid.uuid4()) + '_' + file.filename
        raw_filepath = os.path.join('uploads', unique_filename)
        
        os.makedirs('uploads', exist_ok=True)
        with open(raw_filepath, 'wb') as f:
            f.write(contents)
        
        processed_filename = 'proc_' + unique_filename
        processed_filepath = os.path.join('uploads', processed_filename)
        
        pre_process(raw_filepath, processed_filepath)
        
        df = pd.read_csv(processed_filepath)
        
        expected_columns = [
            'location',
            'relative_humidity_2m',
            'dew_point_2m ',
            'cloud_cover ',
            'cloud_cover_low ',
            'cloud_cover_mid ',
            'cloud_cover_highh',
            'wind_speed_10m ',
            'wind_direction_10m ',
            'wind_gusts_10m ',
            'wind_direction_100m ',
            'wind_speed_100m ',
            'pressure_msl ',
            'surface_pressure ',
            'rain ',
            'day_sin',
            'day_cos',
            'hour_sin',
            'hour_cos'
        ]
        
        available_columns = [col for col in expected_columns if col in df.columns]
        
        if len(available_columns) == 0:
            raise HTTPException(status_code=400, detail="No matching columns found in CSV. Please ensure CSV has preprocessed column names.")
        
        input_data = pd.DataFrame()
        for col in available_columns:
            input_data[col] = df[col]
        
        predictions = pipeline2.predict(input_data)
        df['temperature_prediction_celsius'] = predictions
        df['temperature_prediction_fahrenheit'] = predictions * 9/5 + 32
        
        df.to_csv(processed_filepath, index=False)
        
        return {"filename": processed_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/temperature/download/{filename}")
async def download_temperature_results(filename: str):
    try:
        filepath = os.path.join('uploads', filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=filepath,
            filename=f"temperature_predictions_{filename}",
            media_type='text/csv'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rain/results")
async def rain_results(filename: str, request: Request):
    try:
        filepath = os.path.join('uploads', filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        df = pd.read_csv(filepath)
        
        expected_columns = [
            'temperature_2m ',
            'relative_humidity_2m',
            'dew_point_2m ',
            'cloud_cover ',
            'cloud_cover_low ',
            'cloud_cover_mid ',
            'cloud_cover_highh',
            'wind_speed_10m ',
            'wind_direction_10m ',
            'wind_gusts_10m ',
            'wind_direction_100m ',
            'wind_speed_100m ',
            'pressure_msl ',
            'surface_pressure '
        ]
        
        available_columns = [col for col in expected_columns if col in df.columns]
        
        if len(available_columns) == 0:
            raise HTTPException(status_code=400, detail="No matching columns found in CSV. Please ensure CSV has preprocessed column names.")
        
        input_data = df[available_columns].copy()
        
        predictions = pipeline1.predict(input_data)
        df['rain_prediction'] = predictions
        
        df.to_csv(filepath, index=False)
        
        columns = df.columns.tolist()
        rows = []
        for idx, row in df.iterrows():
            rows.append(dict(row))
        
        return templates.TemplateResponse("rain_results.html", {
            "request": request,
            "filename": filename,
            "columns": columns,
            "rows": rows
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/temperature/results")
async def temperature_results(filename: str, request: Request):
    try:
        filepath = os.path.join('uploads', filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        df = pd.read_csv(filepath)
        
        expected_columns = [
            'location',
            'relative_humidity_2m',
            'dew_point_2m ',
            'cloud_cover ',
            'cloud_cover_low ',
            'cloud_cover_mid ',
            'cloud_cover_highh',
            'wind_speed_10m ',
            'wind_direction_10m ',
            'wind_gusts_10m ',
            'wind_direction_100m ',
            'wind_speed_100m ',
            'pressure_msl ',
            'surface_pressure ',
            'rain ',
            'day_sin',
            'day_cos',
            'hour_sin',
            'hour_cos'
        ]
        
        available_columns = [col for col in expected_columns if col in df.columns]
        
        if len(available_columns) == 0:
            raise HTTPException(status_code=400, detail="No matching columns found in CSV. Please ensure CSV has preprocessed column names.")
        
        input_data = pd.DataFrame()
        for col in available_columns:
            input_data[col] = df[col]
        
        predictions = pipeline2.predict(input_data)
        df['temperature_prediction_celsius'] = predictions
        df['temperature_prediction_fahrenheit'] = predictions * 9/5 + 32
        
        df.to_csv(filepath, index=False)
        
        columns = df.columns.tolist()
        rows = []
        for idx, row in df.iterrows():
            rows.append(dict(row))
        
        return templates.TemplateResponse("temperature_results.html", {
            "request": request,
            "filename": filename,
            "columns": columns,
            "rows": rows
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/temperature")
async def temperature_interface():
    return FileResponse('static/temperature.html')

app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- Level 4 (Daily accidents) ----------------

@app.post("/level4/upload")
async def level4_upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        unique = str(uuid.uuid4()) + '_' + file.filename
        raw_path = os.path.join('uploads', unique)
        os.makedirs('uploads', exist_ok=True)
        with open(raw_path, 'wb') as f:
            f.write(contents)

        # Read raw hourly data
        df = pd.read_csv(raw_path)

        required_base = [
            'location', 'time',
            'temperature_2m ', 'relative_humidity_2m', 'dew_point_2m ', 'rain ',
            'cloud_cover ', 'cloud_cover_low ', 'cloud_cover_mid ', 'cloud_cover_highh',
            'wind_speed_10m ', 'wind_direction_10m ', 'wind_gusts_10m ',
            'wind_direction_100m ', 'wind_speed_100m ',
            'pressure_msl ', 'surface_pressure '
        ]

        missing = [c for c in ['location', 'time'] if c not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")

        # Parse time and get date
        df['time'] = pd.to_datetime(df['time'])
        df['date'] = df['time'].dt.date

        # Keep only known numeric feature columns that exist
        numeric_cols = [c for c in required_base if c in df.columns and c not in ['location', 'time']]

        # Aggregate to daily by mean across available hours (works even with <24 rows/day)
        agg_map = {c: 'mean' for c in numeric_cols}
        daily = df.groupby(['location', 'date'], as_index=False).agg(agg_map)
        # Optional: keep a count of hourly rows per day (not required for predictions)
        counts = df.groupby(['location', 'date']).size().reset_index(name='rows')
        daily = daily.merge(counts, on=['location', 'date'], how='left')
        if daily.empty:
            raise HTTPException(status_code=400, detail="No daily aggregates could be computed from the provided data.")

        # One-hot encode location to match model features
        daily_ohe = pd.get_dummies(daily, columns=['location'], drop_first=False, dtype=int)

        # Ensure all expected features exist
        expected_features = list(getattr(model4, 'feature_names_in_', []))
        # Build the input X by adding missing columns as 0
        for feat in expected_features:
            if feat not in daily_ohe.columns:
                daily_ohe[feat] = 0

        X = daily_ohe[expected_features].copy()
        preds = model4.predict(X)
        # Round to non-negative integers
        daily['accidents_prediction'] = pd.Series(preds).round().clip(lower=0).astype(int)
        # Derived resource planning column
        daily['cars_needed'] = (daily['accidents_prediction'] * 3).astype(int)
        # Keep 'rows' to show how many hourly records were used (informational)

        proc_name = 'proc_level4_' + unique
        proc_path = os.path.join('uploads', proc_name)
        # Save only readable daily data with predictions
        daily.to_csv(proc_path, index=False)

        return {"filename": proc_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/level4/results")
async def level4_results(filename: str, request: Request):
    try:
        path = os.path.join('uploads', filename)
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="File not found")
        df = pd.read_csv(path)

        # Prepare rows/columns for template
        columns = []
        for col in ['date', 'location', 'accidents_prediction', 'cars_needed']:
            if col in df.columns:
                columns.append(col)
        if not columns:
            # Fallback: just show whatever exists
            columns = df.columns.tolist()
        rows = [dict(r) for _, r in df[columns].iterrows()]

        return templates.TemplateResponse("level4_results.html", {
            "request": request,
            "filename": filename,
            "columns": columns,
            "rows": rows
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/level4/download/{filename}")
async def level4_download(filename: str):
    try:
        path = os.path.join('uploads', filename)
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path=path, filename=f"level4_accidents_{filename}", media_type='text/csv')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# UI route for Level 4
@app.get("/level4")
async def level4_interface():
    return FileResponse('static/level4.html')

# ---------------- Level 5 (Next-day predictions: rain, temperature, clouds) ----------------

@app.get("/level5")
async def level5_interface():
    return FileResponse('static/level5.html')

@app.post("/level5/upload")
async def level5_upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        unique = str(uuid.uuid4()) + '_' + file.filename
        raw_path = os.path.join('uploads', unique)
        os.makedirs('uploads', exist_ok=True)
        with open(raw_path, 'wb') as f:
            f.write(contents)

        # Preprocess to add cyclical features (day/hour) and clean data
        proc_name = 'proc_level5_' + unique
        proc_path = os.path.join('uploads', proc_name)
        pre_process(raw_path, proc_path)

        df = pd.read_csv(proc_path)

        # Build inputs for each model based on its expected features
        def predict_with(model, out_col_name):
            feats = list(getattr(model, 'feature_names_in_', []))
            # Add any missing feature as 0 (useful for one-hot cols if any)
            for c in feats:
                if c not in df.columns:
                    df[c] = 0
            X = df[feats].copy()
            preds = model.predict(X)
            df[out_col_name] = preds

        # 5.1 Rain (classification or probability -> coerce to bool/int)
        predict_with(model51, 'next_day_rain_pred_raw')
        # Ensure boolean-ish output
        df['next_day_rain_pred'] = df['next_day_rain_pred_raw'].astype(float).round().clip(lower=0).astype(int)
        df = df.drop(columns=['next_day_rain_pred_raw'])

        # 5.2 Temperature (Celsius)
        predict_with(model52, 'next_day_temp_c')
        # 5.3 Cloud cover (%)
        predict_with(model53, 'next_day_cloud_cover')

        df.to_csv(proc_path, index=False)
        return {"filename": proc_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/level5/results")
async def level5_results(filename: str, request: Request):
    try:
        path = os.path.join('uploads', filename)
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="File not found")
        df = pd.read_csv(path)

        # Choose a compact subset to display if present
        display_cols = []
        for col in [
            'location', 'day_sin', 'day_cos', 'hour_sin', 'hour_cos',
            'next_day_rain_pred', 'next_day_temp_c', 'next_day_cloud_cover']:
            if col in df.columns:
                display_cols.append(col)
        if not display_cols:
            display_cols = df.columns.tolist()
        rows = [dict(r) for _, r in df[display_cols].iterrows()]

        return templates.TemplateResponse("level5_results.html", {
            "request": request,
            "filename": filename,
            "columns": display_cols,
            "rows": rows
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/level5/download/{filename}")
async def level5_download(filename: str):
    try:
        path = os.path.join('uploads', filename)
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path=path, filename=f"level5_predictions_{filename}", media_type='text/csv')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
