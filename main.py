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
