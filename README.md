# Weather and Clothing Recommendation MCP Server

An MCP (Model Context Protocol) server that provides weather information and clothing recommendations based on current weather conditions.

## Features

- **Weather Information**: Fetches real-time weather data for any city using the Open-Meteo API
- **Clothing Recommendations**: Provides intelligent clothing suggestions based on temperature, wind, humidity, and weather conditions
- **Activity Advice**: Generates structured prompts for AI assistants to provide activity-specific guidance
- **Two Tools Available**:
  - `get_weather`: Get current weather for a city
  - `get_clothing_recommendation`: Get weather and clothing advice
- **Prompt Template**: `weather_advice` - generates structured prompts with weather data

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Easiest - Recommended!)

Run the FastAPI web application with a beautiful GUI:
```bash
python app.py
```

Then open your browser to: **http://localhost:8000**

Features:
- Beautiful, responsive web interface
- Enter city name and activity
- Get instant weather and clothing recommendations
- Works on desktop and mobile

### Quick Test (No MCP Required)

Test the weather and clothing recommendations directly:
```bash
python simple_test.py
```

This will let you:
- Test a single city (Paris by default)
- Test multiple cities at once
- Enter city names interactively

### Running the MCP Server

Run the MCP server directly:
```bash
python weather_server.py
```

### Testing with MCP Client

Run the client example to see how MCP works:
```bash
python client_example.py
```

This demonstrates:
- Listing available tools and prompts
- Calling tools to get weather data
- Using prompts to generate structured advice
- Full AI assistant flow (requires `ANTHROPIC_API_KEY` environment variable)

### Configuring with Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/absolute/path/to/weather_server.py"]
    }
  }
}
```

### Available Tools

#### 1. get_weather
Get current weather information for a city.

**Input:**
```json
{
  "city": "Paris"
}
```

**Output:**
```json
{
  "city": "Paris",
  "weather": {
    "temperature": 15.2,
    "wind_speed": 12.5,
    "humidity": 65,
    "weather_code": 2,
    "weather_description": "Partly cloudy"
  }
}
```

#### 2. get_clothing_recommendation
Get weather and clothing recommendations for a city.

**Input:**
```json
{
  "city": "New York"
}
```

**Output:**
```json
{
  "city": "New York",
  "weather": {
    "temperature": 8.5,
    "wind_speed": 15.0,
    "humidity": 70,
    "weather_code": 61,
    "weather_description": "Slight rain"
  },
  "clothing_recommendation": {
    "layers": [
      "Long-sleeve shirt",
      "Sweater or light jacket",
      "Medium coat"
    ],
    "accessories": [
      "Umbrella",
      "Raincoat or waterproof jacket",
      "Light hat or beanie",
      "Light gloves"
    ],
    "footwear": "Waterproof shoes or boots",
    "general_advice": [
      "A light jacket should be sufficient",
      "Rain expected - bring waterproof gear"
    ]
  }
}
```

### Available Prompts

#### weather_advice
Generates a structured prompt with weather information and activity advice.

**Arguments:**
- `city` (required): Name of the city
- `activity` (optional): Activity you're planning (e.g., "hiking", "running", "sightseeing")

**Example Usage in Claude:**

User asks: "Should I go hiking in Paris today?"

Claude will use the MCP prompt to fetch weather data and receive a structured prompt like:

```
Based on current weather in Paris, provide advice for: hiking

Weather Conditions:
- Temperature: 15.2°C
- Conditions: Partly cloudy
- Wind Speed: 12.5 km/h
- Humidity: 65%

Clothing Recommendations:
Layers:
  - T-shirt or long-sleeve shirt
  - Light jacket or cardigan

Accessories:
  - Sunglasses

Footwear: Comfortable shoes or sneakers

General Advice:
  - Pleasant temperature, light layers recommended

Please provide:
1. Is the weather suitable for hiking?
2. What precautions should be taken?
3. What is the best time of day for this activity?
4. Any alternative suggestions if conditions aren't ideal?
```

## How It Works

1. **City Lookup**: Converts city names to coordinates using Open-Meteo Geocoding API
2. **Weather Fetch**: Retrieves current weather data (temperature, wind, humidity, conditions)
3. **Clothing Logic**: Analyzes weather to recommend:
   - Appropriate layers based on temperature
   - Wind-resistant gear for strong winds
   - Waterproof items for rain/snow
   - Sun protection for clear, warm weather
4. **Structured Output**: Provides formatted data for AI assistants to give personalized advice

## API Used

- **Open-Meteo**: Free weather API (no API key required)
  - Geocoding API: Converts city names to coordinates
  - Weather API: Provides current weather data

## Temperature-Based Recommendations

- **Below 0°C**: Heavy winter gear, thermal layers, insulated boots
- **0-10°C**: Medium coat, sweater, closed-toe shoes
- **10-20°C**: Light jacket, comfortable shoes
- **Above 20°C**: Light clothing, sun protection

## Requirements

- Python 3.8+
- httpx: For API requests
- mcp: Model Context Protocol library

## License

MIT
