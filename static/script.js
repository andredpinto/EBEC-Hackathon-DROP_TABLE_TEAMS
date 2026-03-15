let predictionTimeout = null;

const sliderIds = [
    'temperature_2m',
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
    'surface_pressure'
];

function getSliderValues() {
    const data = {};
    sliderIds.forEach(id => {
        data[id] = parseFloat(document.getElementById(id).value);
    });
    return data;
}

function updateSliderDisplays() {
    sliderIds.forEach(id => {
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
            } else {
                display.textContent = value.toFixed(1) + '°C';
            }
        }
    });
}

async function predictRain() {
    const data = getSliderValues();
    
    try {
        const response = await fetch('/rain/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        const rainIcon = document.getElementById('rainIcon');
        const rainText = document.getElementById('rainText');
        const probabilityFill = document.getElementById('probabilityFill');
        const probabilityText = document.getElementById('probabilityText');
        
        if (result.rain_prediction) {
            // rainIcon.className = 'bi bi-cloud-rain';
            rainText.textContent = 'Raining';
            probabilityFill.classList.remove('bg-info', 'bg-warning');
            probabilityFill.classList.add('bg-info');
            probabilityFill.style.width = '100%';
            // probabilityText.textContent = 'High probability of rain detected';
        } else {
            // rainIcon.className = 'bi bi-sun';
            rainText.textContent = 'Not Raining';
            probabilityFill.classList.remove('bg-info', 'bg-warning');
            probabilityFill.classList.add('bg-warning');
            probabilityFill.style.width = '100%';
            // probabilityText.textContent = 'Low probability of rain';
        }
        
    } catch (error) {
        console.error('Error predicting rain:', error);
        const rainText = document.getElementById('rainText');
        rainText.textContent = 'Error predicting';
    }
}

function debouncedPrediction() {
    if (predictionTimeout) {
        clearTimeout(predictionTimeout);
    }
    
    predictionTimeout = setTimeout(function() {
        predictRain();
    }, 300);
}

function initializeSliders() {
    sliderIds.forEach(id => {
        const slider = document.getElementById(id);
        
        if (slider) {
            slider.addEventListener('input', function() {
                updateSliderDisplays();
                debouncedPrediction();
            });
        }
    });
    
    updateSliderDisplays();
    predictRain();
}

function setPreset(type) {
    const presets = {
        rainy: {
            temperature_2m: 12,
            relative_humidity_2m: 90,
            dew_point_2m: 11,
            cloud_cover: 95,
            cloud_cover_low: 90,
            cloud_cover_mid: 85,
            cloud_cover_highh: 80,
            wind_speed_10m: 15,
            wind_direction_10m: 180,
            wind_gusts_10m: 25,
            wind_direction_100m: 175,
            wind_speed_100m: 20,
            pressure_msl: 1008,
            surface_pressure: 1007
        },
        sunny: {
            temperature_2m: 22,
            relative_humidity_2m: 40,
            dew_point_2m: 8,
            cloud_cover: 15,
            cloud_cover_low: 10,
            cloud_cover_mid: 12,
            cloud_cover_highh: 8,
            wind_speed_10m: 5,
            wind_direction_10m: 90,
            wind_gusts_10m: 8,
            wind_direction_100m: 85,
            wind_speed_100m: 7,
            pressure_msl: 1022,
            surface_pressure: 1021
        },
        stormy: {
            temperature_2m: 16,
            relative_humidity_2m: 95,
            dew_point_2m: 15,
            cloud_cover: 100,
            cloud_cover_low: 95,
            cloud_cover_mid: 98,
            cloud_cover_highh: 90,
            wind_speed_10m: 25,
            wind_direction_10m: 220,
            wind_gusts_10m: 45,
            wind_direction_100m: 210,
            wind_speed_100m: 35,
            pressure_msl: 1005,
            surface_pressure: 1004
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
        updateSliderDisplays();
        predictRain();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeSliders();
});

async function uploadCSV() {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a CSV file to upload.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/rain/upload', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            window.location.href = '/rain/results?filename=' + result.filename;
        } else {
            const error = await response.json();
            alert('Error uploading file: ' + error.detail);
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error uploading file. Please try again.');
    }
}
