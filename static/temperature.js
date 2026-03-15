let tempPredictionTimeout = null;

const tempSliderIds = [
    'relative_humidity_2m',
    'dew_point_2m',
    'cloud_cover',
    'cloud_cover_low',
    'cloud_cover_mid',
    'cloud_cover_highh',
    'wind_speed_10m',
    'wind_direction_10m',
    'wind_gusts_10m',
    'wind_direction_100m',
    'wind_speed_100m',
    'pressure_msl',
    'surface_pressure',
    'rain'
];

function getTempSliderValues() {
    const data = {};
    tempSliderIds.forEach(id => {
        data[id] = parseFloat(document.getElementById(id).value);
    });
    
    const now = new Date();
    const hour = now.getHours();
    const dayOfYear = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 86400000);
    
    data['day_sin'] = Math.sin((dayOfYear / 365) * 2 * Math.PI);
    data['day_cos'] = Math.cos((dayOfYear / 365) * 2 * Math.PI);
    data['hour_sin'] = Math.sin((hour / 24) * 2 * Math.PI);
    data['hour_cos'] = Math.cos((hour / 24) * 2 * Math.PI);
    data['location'] = document.getElementById('location').value;
    
    return data;
}

function updateTempSliderDisplays() {
    tempSliderIds.forEach(id => {
        const slider = document.getElementById(id);
        const display = document.getElementById(`${id}_value`);
        if (slider && display) {
            const value = parseFloat(slider.value);
            
            if (id.includes('humidity') || id.includes('cloud')) {
                display.textContent = Math.round(value) + '%';
            } else if (id.includes('direction')) {
                display.textContent = Math.round(value) + '°';
            } else if (id.includes('pressure')) {
                display.textContent = value.toFixed(1) + ' hPa';
            } else if (id.includes('speed') || id.includes('gusts')) {
                display.textContent = value.toFixed(1) + ' m/s';
            } else if (id === 'rain') {
                display.textContent = value.toFixed(1) + ' mm';
            }
        }
    });
    
    const locationSelect = document.getElementById('location');
    const locationDisplay = document.getElementById('location_value');
    if (locationSelect && locationDisplay) {
        locationDisplay.textContent = locationSelect.value;
    }
}

async function predictTemperature() {
    const data = getTempSliderValues();
    
    try {
        const response = await fetch('/temperature/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        const tempIcon = document.getElementById('tempIcon');
        const tempText = document.getElementById('tempText');
        const tempFill = document.getElementById('tempFill');
        const tempFahrenheit = document.getElementById('tempFahrenheit');
        // tempIcon.className = 'bi bi-thermometer';
        tempText.textContent = result.temperature_celsius + '°C';
        const percentage = Math.min(100, Math.max(0, (parseFloat(result.temperature_celsius) + 10) / 60 * 100));
        tempFill.style.width = percentage + '%';
        tempFahrenheit.textContent = 'Fahrenheit: ' + result.temperature_fahrenheit + '°F';
        
    } catch (error) {
        console.error('Error predicting temperature:', error);
        const tempText = document.getElementById('tempText');
        tempText.textContent = 'Error predicting';
    }
}

function debouncedTempPrediction() {
    if (tempPredictionTimeout) {
        clearTimeout(tempPredictionTimeout);
    }
    
    tempPredictionTimeout = setTimeout(function() {
        predictTemperature();
    }, 300);
}

function initializeTempSliders() {
    tempSliderIds.forEach(id => {
        const slider = document.getElementById(id);
        
        if (slider) {
            slider.addEventListener('input', function() {
                updateTempSliderDisplays();
                debouncedTempPrediction();
            });
        }
    });
    
    const locationSelect = document.getElementById('location');
    if (locationSelect) {
        locationSelect.addEventListener('change', function() {
            updateTempSliderDisplays();
            debouncedTempPrediction();
        });
    }
    
    updateTempSliderDisplays();
    predictTemperature();
}

function setTempPreset(type) {
    const presets = {
        cold: {
            temperature_2m: 5,
            relative_humidity_2m: 80,
            dew_point_2m: 2,
            cloud_cover: 60,
            cloud_cover_low: 50,
            cloud_cover_mid: 55,
            cloud_cover_highh: 40,
            wind_speed_10m: 12,
            wind_direction_10m: 330,
            wind_gusts_10m: 20,
            wind_direction_100m: 325,
            wind_speed_100m: 18,
            pressure_msl: 1022,
            surface_pressure: 1021,
            rain: 2.0
        },
        moderate: {
            temperature_2m: 15,
            relative_humidity_2m: 65,
            dew_point_2m: 8,
            cloud_cover: 45,
            cloud_cover_low: 35,
            cloud_cover_mid: 40,
            cloud_cover_highh: 30,
            wind_speed_10m: 8,
            wind_direction_10m: 180,
            wind_gusts_10m: 15,
            wind_direction_100m: 175,
            wind_speed_100m: 12,
            pressure_msl: 1015,
            surface_pressure: 1014,
            rain: 0.5
        },
        warm: {
            temperature_2m: 28,
            relative_humidity_2m: 40,
            dew_point_2m: 15,
            cloud_cover: 20,
            cloud_cover_low: 15,
            cloud_cover_mid: 18,
            cloud_cover_highh: 12,
            wind_speed_10m: 5,
            wind_direction_10m: 90,
            wind_gusts_10m: 8,
            wind_direction_100m: 85,
            wind_speed_100m: 7,
            pressure_msl: 1018,
            surface_pressure: 1017,
            rain: 0.0
        }
    };
    
    const preset = presets[type];
    if (preset) {
        Object.keys(preset).forEach(id => {
            const slider = document.getElementById(id);
            if (slider) {
                slider.value = preset[id];
            }
        });
        updateTempSliderDisplays();
        predictTemperature();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeTempSliders();
});
