# MCP Architecture Explained

## What is MCP?

**Model Context Protocol (MCP)** is a way for AI assistants to connect to external tools and data sources. Think of it as a bridge between an AI (like Claude) and specialized services (like our weather service).

## Components

### 1. **MCP Server** (`weather_server.py`)
The backend service that:
- Fetches weather data from Open-Meteo API
- Calculates clothing recommendations
- Exposes **Tools** and **Prompts** for clients to use

### 2. **MCP Client** (`client_example.py`)
A program that:
- Connects to the MCP server
- Calls tools to get data
- Requests prompts for structured information
- Can pass data to AI assistants

### 3. **AI Assistant** (Claude, ChatGPT, etc.)
Uses the MCP client to:
- Access real-time data
- Get structured prompts
- Provide intelligent responses to users

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUESTION                            │
│              "Should I go hiking in Paris today?"                │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AI ASSISTANT                              │
│  Recognizes: User wants weather advice for hiking in Paris      │
│  Decision: I need current weather data!                         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP CLIENT                                  │
│  Calls: get_prompt("weather_advice", {                          │
│           "city": "Paris",                                       │
│           "activity": "hiking"                                   │
│         })                                                       │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP SERVER                                  │
│                                                                  │
│  Step 1: Convert "Paris" → coordinates (48.85°N, 2.35°E)       │
│  Step 2: Fetch weather from Open-Meteo API                      │
│          • Temperature: 15.2°C                                  │
│          • Conditions: Partly cloudy                            │
│          • Wind: 12.5 km/h                                      │
│          • Humidity: 65%                                        │
│  Step 3: Calculate clothing recommendations                     │
│          • Layers: T-shirt, light jacket                        │
│          • Accessories: Sunglasses                              │
│          • Footwear: Comfortable shoes                          │
│  Step 4: Build structured prompt                                │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STRUCTURED PROMPT                             │
│                                                                  │
│  "Based on current weather in Paris, advise for: hiking         │
│                                                                  │
│   Weather Conditions:                                           │
│   - Temperature: 15.2°C                                         │
│   - Conditions: Partly cloudy                                   │
│   - Wind Speed: 12.5 km/h                                       │
│   - Humidity: 65%                                               │
│                                                                  │
│   Clothing Recommendations:                                     │
│   Layers: T-shirt, light jacket                                 │
│   Accessories: Sunglasses                                       │
│   Footwear: Comfortable shoes                                   │
│                                                                  │
│   Please provide:                                               │
│   1. Is it suitable for hiking?                                 │
│   2. Precautions needed?                                        │
│   3. Best time of day?                                          │
│   4. Alternative suggestions?"                                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI PROCESSES PROMPT                          │
│                                                                  │
│  AI reads the structured data and generates natural response:   │
│                                                                  │
│  "Great news! 15°C with partly cloudy skies is perfect for     │
│   hiking in Paris today. The conditions are ideal - not too    │
│   hot, not too cold. Here's what I recommend:                  │
│                                                                  │
│   Clothing: Wear a t-shirt with a light jacket you can tie    │
│   around your waist if you get warm. Bring sunglasses as the  │
│   sun may peek through the clouds.                             │
│                                                                  │
│   Best time: Morning (8-10am) or late afternoon (4-6pm) when  │
│   temperatures are most comfortable.                            │
│                                                                  │
│   Precautions: Stay hydrated and check the forecast for any   │
│   changes. The light wind will keep you comfortable.           │
│                                                                  │
│   Have a wonderful hike! 🥾"                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Two Ways to Use This Project

### Option A: Direct Testing (Simple)
```bash
python simple_test.py
```
- No MCP required
- Tests weather fetching directly
- Good for development and debugging

### Option B: Full MCP Flow (Complete)
```bash
# Terminal 1: Run server
python weather_server.py

# Terminal 2: Run client
python client_example.py
```
- Full MCP protocol
- Shows how AI assistants integrate
- Demonstrates prompts and tools

### Option C: With Claude Desktop (Production)
1. Configure `claude_desktop_config.json`
2. Claude automatically connects to your server
3. Users ask questions naturally
4. Claude uses your weather tools behind the scenes

## Key Concepts

### Tools
Functions that the AI can call directly:
- `get_weather(city)` - Get current weather
- `get_clothing_recommendation(city)` - Get weather + clothing advice

### Prompts
Templates that structure information for the AI:
- `weather_advice(city, activity)` - Complete structured prompt with weather data and questions

### Why Use MCP?

**Without MCP:**
- AI has outdated information (knowledge cutoff)
- Can't access real-time data
- Generic responses

**With MCP:**
- AI accesses live weather data
- Provides current, accurate information
- Gives specific, actionable advice

## Example Interactions

### Using Tools Directly
```python
# AI calls tool
result = call_tool("get_weather", {"city": "Paris"})

# Gets JSON back
{
  "temperature": 15.2,
  "conditions": "Partly cloudy",
  ...
}

# AI formats response naturally
"The current temperature in Paris is 15.2°C with partly cloudy skies."
```

### Using Prompts
```python
# AI requests prompt
prompt = get_prompt("weather_advice", {
  "city": "Paris",
  "activity": "hiking"
})

# Gets structured prompt with all data + questions
# AI processes the complete context and generates comprehensive advice
```

## Files Overview

| File | Purpose |
|------|---------|
| `weather_server.py` | MCP server - provides tools and prompts |
| `client_example.py` | MCP client - demonstrates how to connect and use the server |
| `simple_test.py` | Standalone testing - no MCP needed |
| `requirements.txt` | Python dependencies |
| `README.md` | User documentation |
| `ARCHITECTURE.md` | This file - explains how everything works |
