"""
FastAPI Weather and Clothing Recommendation Application

A web application that provides weather information and clothing recommendations
through a user-friendly web interface. Users enter a city name and receive
current weather data with appropriate clothing suggestions.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from weather_server import (
    get_coordinates,
    get_weather,
    recommend_clothing
)


# Initialize FastAPI app
app = FastAPI(
    title="Weather & Clothing Recommendation API",
    description="Get weather information and clothing recommendations for any city",
    version="1.0.0"
)


class CityRequest(BaseModel):
    """
    Request model for city weather lookup.

    Attributes:
        city: Name of the city to get weather for
        activity: Optional activity the user is planning
    """
    city: str
    activity: Optional[str] = "general outdoor activities"


class WeatherResponse(BaseModel):
    """
    Response model containing weather and clothing data.

    Attributes:
        city: Name of the city
        coordinates: Geographic coordinates (latitude, longitude)
        weather: Current weather information
        clothing: Clothing recommendations based on weather
        activity: Activity the recommendations are for
    """
    city: str
    coordinates: dict
    weather: dict
    clothing: dict
    activity: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serve the main HTML page.

    Returns the web interface where users can input city names
    and view weather and clothing recommendations.
    """
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather & Clothing Advisor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }

        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .input-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 1.1em;
        }

        input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: all 0.3s;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #fee;
            border: 2px solid #fcc;
            color: #c33;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }

        .results {
            margin-top: 30px;
            display: none;
        }

        .weather-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
        }

        .weather-card h2 {
            margin-bottom: 15px;
            font-size: 1.8em;
        }

        .weather-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .weather-item {
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }

        .weather-item .label {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }

        .weather-item .value {
            font-size: 1.5em;
            font-weight: bold;
        }

        .clothing-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 15px;
        }

        .clothing-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.4em;
        }

        .clothing-list {
            list-style: none;
        }

        .clothing-list li {
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
        }

        .clothing-list li:last-child {
            border-bottom: none;
        }

        .clothing-list li:before {
            content: "✓";
            display: inline-block;
            width: 25px;
            height: 25px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 25px;
            margin-right: 10px;
            font-weight: bold;
        }

        .advice-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }

        .advice-box p {
            margin: 5px 0;
            color: #856404;
        }

        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }

            h1 {
                font-size: 2em;
            }

            .weather-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌤️ Weather & Clothing Advisor</h1>
        <p class="subtitle">Get weather information and clothing recommendations for any city</p>

        <form id="weatherForm">
            <div class="input-group">
                <label for="city">City Name</label>
                <input
                    type="text"
                    id="city"
                    name="city"
                    placeholder="Enter city name (e.g., Paris, Tokyo, New York)"
                    required
                >
            </div>

            <div class="input-group">
                <label for="activity">Activity (Optional)</label>
                <input
                    type="text"
                    id="activity"
                    name="activity"
                    placeholder="e.g., hiking, running, sightseeing"
                >
            </div>

            <button type="submit" id="submitBtn">Get Weather & Clothing Advice</button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #666;">Fetching weather data...</p>
        </div>

        <div class="error" id="error"></div>

        <div class="results" id="results">
            <div class="weather-card">
                <h2 id="cityName"></h2>
                <p id="activityText"></p>
                <div class="weather-grid">
                    <div class="weather-item">
                        <div class="label">Temperature</div>
                        <div class="value" id="temperature"></div>
                    </div>
                    <div class="weather-item">
                        <div class="label">Conditions</div>
                        <div class="value" id="conditions"></div>
                    </div>
                    <div class="weather-item">
                        <div class="label">Wind Speed</div>
                        <div class="value" id="windSpeed"></div>
                    </div>
                    <div class="weather-item">
                        <div class="label">Humidity</div>
                        <div class="value" id="humidity"></div>
                    </div>
                </div>
            </div>

            <div class="clothing-section">
                <h3>👔 Clothing Layers</h3>
                <ul class="clothing-list" id="layers"></ul>
            </div>

            <div class="clothing-section">
                <h3>🎒 Accessories</h3>
                <ul class="clothing-list" id="accessories"></ul>
            </div>

            <div class="clothing-section">
                <h3>👟 Footwear</h3>
                <p id="footwear" style="padding: 10px 0; font-size: 1.1em;"></p>
            </div>

            <div class="clothing-section">
                <h3>💡 General Advice</h3>
                <div class="advice-box" id="advice"></div>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('weatherForm');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
        const results = document.getElementById('results');
        const submitBtn = document.getElementById('submitBtn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Get form values
            const city = document.getElementById('city').value.trim();
            const activity = document.getElementById('activity').value.trim() || 'general outdoor activities';

            // Hide previous results and errors
            results.style.display = 'none';
            error.style.display = 'none';
            loading.style.display = 'block';
            submitBtn.disabled = true;

            try {
                // Call API
                const response = await fetch('/api/weather', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ city, activity })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to fetch weather data');
                }

                // Display results
                displayResults(data);

            } catch (err) {
                // Show error
                error.textContent = err.message;
                error.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                submitBtn.disabled = false;
            }
        });

        function displayResults(data) {
            // City and activity
            document.getElementById('cityName').textContent = data.city;
            document.getElementById('activityText').textContent = `Activity: ${data.activity}`;

            // Weather data
            document.getElementById('temperature').textContent = `${data.weather.temperature}°C`;
            document.getElementById('conditions').textContent = data.weather.weather_description;
            document.getElementById('windSpeed').textContent = `${data.weather.wind_speed} km/h`;
            document.getElementById('humidity').textContent = `${data.weather.humidity}%`;

            // Clothing layers
            const layersList = document.getElementById('layers');
            layersList.innerHTML = '';
            data.clothing.layers.forEach(layer => {
                const li = document.createElement('li');
                li.textContent = layer;
                layersList.appendChild(li);
            });

            // Accessories
            const accessoriesList = document.getElementById('accessories');
            accessoriesList.innerHTML = '';
            data.clothing.accessories.forEach(accessory => {
                const li = document.createElement('li');
                li.textContent = accessory;
                accessoriesList.appendChild(li);
            });

            // Footwear
            document.getElementById('footwear').textContent = data.clothing.footwear;

            // Advice
            const adviceBox = document.getElementById('advice');
            adviceBox.innerHTML = '';
            data.clothing.general_advice.forEach(tip => {
                const p = document.createElement('p');
                p.textContent = `• ${tip}`;
                adviceBox.appendChild(p);
            });

            // Show results
            results.style.display = 'block';
            results.scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
    """


@app.post("/api/weather", response_model=WeatherResponse)
async def get_weather_recommendation(request: CityRequest):
    """
    Get weather information and clothing recommendations for a city.

    This endpoint fetches current weather data and generates appropriate
    clothing recommendations based on temperature, wind, humidity, and
    weather conditions.

    Args:
        request: CityRequest containing city name and optional activity

    Returns:
        WeatherResponse with complete weather and clothing data

    Raises:
        HTTPException: If city is not found or weather data cannot be fetched
    """
    try:
        # Get coordinates for the city
        latitude, longitude = await get_coordinates(request.city)

        # Fetch weather data
        weather = await get_weather(latitude, longitude)

        # Get clothing recommendations
        clothing = recommend_clothing(weather)

        # Build response
        return WeatherResponse(
            city=request.city,
            coordinates={
                "latitude": latitude,
                "longitude": longitude
            },
            weather=weather,
            clothing=clothing,
            activity=request.activity
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
        Status message indicating the API is operational
    """
    return {"status": "healthy", "message": "Weather API is running"}


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║        Weather & Clothing Recommendation Web Application         ║
║                                                                  ║
║  Server starting on: http://localhost:8000                      ║
║  API Documentation: http://localhost:8000/docs                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=8000)
