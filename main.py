from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="Weather Prediction API")

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

@app.get("/temperature")
async def temperature_interface():
    return FileResponse('static/temperature.html')

app.mount("/static", StaticFiles(directory="static"), name="static")
