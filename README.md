# Weather and Clothing Recommendation System

An AI-powered MCP (Model Context Protocol) server that provides real-time weather information and intelligent clothing recommendations using OpenAI's GPT-4o-mini.

## 🌟 Features

- **🌤️ Real-Time Weather Data**: Fetches current weather from Open-Meteo API (no API key required)
- **🤖 AI-Powered Recommendations**: Uses OpenAI GPT-4o-mini for intelligent clothing suggestions
- **🎨 Beautiful Web Interface**: Modern, responsive FastAPI web application
- **🔌 MCP Integration**: Works with AI assistants like Claude Desktop
- **📱 Activity-Specific Advice**: Tailored recommendations for hiking, running, etc.
- **🔄 Fallback Logic**: Continues working even when AI APIs are unavailable

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Paulino-Cristovao/mcp_weather_and_cloth_recommendation.git
cd mcp_weather_and_cloth_recommendation

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Note**: Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)

### 3. Run the Application

#### Web Interface (Recommended!)

```bash
python app.py
```

Open your browser to: **http://localhost:8000**

![Web Interface](https://img.shields.io/badge/Interface-Beautiful-brightgreen)

#### Command Line Test

```bash
python simple_test.py
```

## 📖 Usage Examples

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

## 🏗️ Architecture

```
User Question → AI Assistant → MCP Client → MCP Server → APIs
                                              ├─ Open-Meteo (Weather)
                                              └─ OpenAI (Recommendations)
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation.

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, FastAPI
- **AI**: OpenAI GPT-4o-mini
- **Weather API**: Open-Meteo (free, no key required)
- **MCP**: Model Context Protocol for AI integration
- **Frontend**: HTML, CSS, JavaScript (embedded in FastAPI)

## 📦 Project Structure

```
mcp_weather_and_cloth_recommendation/
├── app.py                 # FastAPI web application
├── weather_server.py      # MCP server implementation
├── client_example.py      # MCP client demo
├── simple_test.py         # Standalone testing script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── README.md              # This file
└── ARCHITECTURE.md        # Architecture documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Weather data provided by [Open-Meteo](https://open-meteo.com/)
- AI powered by [OpenAI](https://openai.com/)
- Built with [FastAPI](https://fastapi.tiangolo.com/)

## 📧 Contact

Created by [Paulino Cristovao](https://github.com/Paulino-Cristovao)
