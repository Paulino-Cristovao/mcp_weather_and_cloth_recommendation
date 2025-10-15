"""
MCP Weather and Clothing Recommendation Server

This server provides weather information for cities and recommends appropriate
clothing based on current weather conditions. It uses the Open-Meteo API for
weather data and provides structured prompts for AI assistants.
"""

import asyncio
import json
import os
from typing import Any
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Load environment variables from .env file
load_dotenv()

# Initialize the MCP server
server = Server("weather-clothing-server")

# Initialize OpenAI client (only if API key is available)
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None


async def get_coordinates(city_name: str) -> tuple[float, float]:
    """
    Convert a city name to geographic coordinates (latitude, longitude).

    Uses the Open-Meteo Geocoding API to find the coordinates of a city.

    Args:
        city_name: Name of the city to look up

    Returns:
        A tuple containing (latitude, longitude) coordinates

    Raises:
        ValueError: If the city cannot be found
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city_name, "count": 1, "language": "en", "format": "json"}
        )
        data = response.json()

        if not data.get("results"):
            raise ValueError(f"City '{city_name}' not found")

        result = data["results"][0]
        return result["latitude"], result["longitude"]


async def get_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """
    Fetch current weather data for given coordinates.

    Retrieves temperature, wind speed, humidity, and weather conditions
    from the Open-Meteo API.

    Args:
        latitude: Geographic latitude
        longitude: Geographic longitude

    Returns:
        Dictionary containing weather information with keys:
        - temperature: Current temperature in Celsius
        - wind_speed: Wind speed in km/h
        - humidity: Relative humidity percentage
        - weather_code: Numeric weather condition code
        - weather_description: Human-readable weather description
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh"
            }
        )
        data = response.json()

        current = data["current"]
        weather_code = current["weather_code"]

        return {
            "temperature": current["temperature_2m"],
            "wind_speed": current["wind_speed_10m"],
            "humidity": current["relative_humidity_2m"],
            "weather_code": weather_code,
            "weather_description": get_weather_description(weather_code)
        }


def get_weather_description(code: int) -> str:
    """
    Convert a numeric weather code to a human-readable description using AI.

    Uses OpenAI to interpret WMO Weather codes and provide natural descriptions.
    Falls back to a standard dictionary if OpenAI is unavailable.

    Args:
        code: WMO weather code (0-99)

    Returns:
        Text description of the weather condition
    """
    try:
        # Check if OpenAI client is available
        if openai_client is None:
            raise ValueError("OpenAI API key not set")

        # Use OpenAI to generate description
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a weather expert. Convert WMO weather codes to brief, natural weather descriptions. Respond with only the weather description, no extra text."
                },
                {
                    "role": "user",
                    "content": f"What is the weather condition for WMO code {code}? Provide a brief 2-4 word description."
                }
            ],
            temperature=0.3,
            max_tokens=20
        )

        description = response.choices[0].message.content.strip()
        return description

    except Exception:
        # Fallback to hardcoded descriptions
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown weather condition")


def recommend_clothing(weather: dict[str, Any]) -> dict[str, Any]:
    """
    Suggest appropriate clothing based on weather conditions using OpenAI API.

    Uses OpenAI's gpt-4o-mini model to generate intelligent clothing
    recommendations based on current weather data.

    Args:
        weather: Dictionary containing weather data (temperature, wind_speed,
                humidity, weather_code, weather_description)

    Returns:
        Dictionary with clothing recommendations:
        - layers: List of recommended clothing layers
        - accessories: List of recommended accessories
        - footwear: Recommended footwear type
        - general_advice: Additional tips
    """
    # Build detailed prompt for OpenAI
    prompt = f"""You are a professional clothing advisor. Analyze these EXACT weather conditions and provide appropriate clothing recommendations:

CURRENT WEATHER CONDITIONS:
Temperature: {weather['temperature']}°C
Weather Condition: {weather['weather_description']}
Wind Speed: {weather['wind_speed']} km/h
Humidity: {weather['humidity']}%

IMPORTANT GUIDELINES:
- For temperatures BELOW 0°C: Recommend heavy winter gear (thermal underwear, heavy coat, insulated boots)
- For temperatures 0-10°C: Recommend medium layers (sweater, medium coat, closed shoes)
- For temperatures 10-20°C: Recommend light layers (t-shirt, light jacket, comfortable shoes)
- For temperatures ABOVE 20°C: Recommend light clothing (t-shirt, shorts, sandals/light shoes)
- For RAIN/DRIZZLE: MUST include waterproof jacket, umbrella, waterproof footwear
- For SNOW: MUST include heavy winter coat, waterproof boots, warm accessories
- For HIGH WIND (>20 km/h): MUST include windbreaker
- For CLEAR/SUNNY weather with temp >20°C: MUST include sunglasses, hat, sunscreen

Respond with ONLY a JSON object (no markdown, no code blocks):
{{
    "layers": ["specific clothing item 1", "specific clothing item 2"],
    "accessories": ["specific accessory 1", "specific accessory 2"],
    "footwear": "specific footwear recommendation",
    "general_advice": ["specific advice 1", "specific advice 2"]
}}

Base your recommendations STRICTLY on the temperature and weather conditions provided above."""

    try:
        # Check if OpenAI client is available
        if openai_client is None:
            raise ValueError("OpenAI API key not set")

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional clothing advisor. Your recommendations MUST match the exact weather conditions provided. Be specific and practical. Different weather conditions require different clothing. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        # Parse response
        response_text = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        clothing_data = json.loads(response_text)

        # Validate structure
        required_keys = ["layers", "accessories", "footwear", "general_advice"]
        if all(key in clothing_data for key in required_keys):
            return clothing_data
        else:
            raise ValueError("Invalid response structure from OpenAI")

    except Exception as e:
        # Fallback to basic recommendations if API fails
        print(f"Warning: OpenAI API failed ({str(e)}), using fallback recommendations")

        temp = weather["temperature"]
        wind_speed = weather["wind_speed"]
        weather_code = weather["weather_code"]

        layers = []
        accessories = []
        footwear = "Regular shoes"
        advice = []

        # Temperature-based recommendations
        if temp < 0:
            layers = ["Thermal underwear", "Warm sweater or fleece", "Heavy winter coat"]
            accessories.append("Warm hat")
            accessories.append("Insulated gloves")
            accessories.append("Scarf")
            footwear = "Insulated winter boots"
            advice.append("Dress in multiple layers to trap warmth")
        elif temp < 10:
            layers = ["Long-sleeve shirt", "Sweater or light jacket", "Medium coat"]
            accessories.append("Light hat or beanie")
            accessories.append("Light gloves")
            footwear = "Closed-toe shoes or boots"
            advice.append("A light jacket should be sufficient")
        elif temp < 20:
            layers = ["T-shirt or long-sleeve shirt", "Light jacket or cardigan"]
            footwear = "Comfortable shoes or sneakers"
            advice.append("Pleasant temperature, light layers recommended")
        else:
            layers = ["T-shirt or light shirt", "Optional: light cardigan"]
            footwear = "Sandals, sneakers, or light shoes"
            advice.append("Warm weather, dress lightly and stay hydrated")

        # Wind considerations
        if wind_speed > 20:
            accessories.append("Windbreaker or wind-resistant jacket")
            advice.append(f"Strong winds at {wind_speed} km/h - wear wind-resistant clothing")

        # Weather condition recommendations
        if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:  # Rain
            accessories.append("Umbrella")
            accessories.append("Raincoat or waterproof jacket")
            footwear = "Waterproof shoes or boots"
            advice.append("Rain expected - bring waterproof gear")
        elif weather_code in [71, 73, 75, 77, 85, 86]:  # Snow
            accessories.append("Waterproof gloves")
            footwear = "Waterproof insulated boots"
            advice.append("Snow conditions - wear waterproof footwear")
        elif weather_code in [95, 96, 99]:  # Thunderstorm
            accessories.append("Waterproof jacket")
            advice.append("Thunderstorm conditions - stay indoors if possible")

        # Sun protection for clear weather and high temperatures
        if weather_code in [0, 1] and temp > 20:
            accessories.append("Sunglasses")
            accessories.append("Sunscreen")
            accessories.append("Hat for sun protection")

        return {
            "layers": layers,
            "accessories": list(set(accessories)),
            "footwear": footwear,
            "general_advice": advice
        }


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompt templates.

    Returns the prompts that clients can request from this server.
    """
    return [
        types.Prompt(
            name="weather_advice",
            description="Get weather information and activity advice for a city",
            arguments=[
                types.PromptArgument(
                    name="city",
                    description="Name of the city",
                    required=True
                ),
                types.PromptArgument(
                    name="activity",
                    description="Activity you're planning (e.g., hiking, running, sightseeing)",
                    required=False
                )
            ]
        )
    ]


@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a structured prompt with weather data and clothing recommendations.

    Creates a comprehensive prompt that includes current weather information,
    clothing recommendations, and activity-specific advice for AI assistants.

    Args:
        name: Name of the prompt template to use
        arguments: Dictionary containing:
            - city: City name (required)
            - activity: Planned activity (optional)

    Returns:
        A structured prompt containing weather data and recommendations

    Raises:
        ValueError: If required arguments are missing or invalid
    """
    if name != "weather_advice":
        raise ValueError(f"Unknown prompt: {name}")

    if not arguments or "city" not in arguments:
        raise ValueError("City name is required")

    city = arguments["city"]
    activity = arguments.get("activity", "general outdoor activity")

    # Fetch weather data
    try:
        latitude, longitude = await get_coordinates(city)
        weather = await get_weather(latitude, longitude)
        clothing = recommend_clothing(weather)
    except Exception as e:
        raise ValueError(f"Failed to fetch weather data: {str(e)}")

    # Build structured prompt
    prompt_text = f"""Based on current weather in {city}, provide advice for: {activity}

Weather Conditions:
- Temperature: {weather['temperature']}°C
- Conditions: {weather['weather_description']}
- Wind Speed: {weather['wind_speed']} km/h
- Humidity: {weather['humidity']}%

Clothing Recommendations:
Layers:
{chr(10).join(f'  - {layer}' for layer in clothing['layers'])}

Accessories:
{chr(10).join(f'  - {item}' for item in clothing['accessories'])}

Footwear: {clothing['footwear']}

General Advice:
{chr(10).join(f'  - {tip}' for tip in clothing['general_advice'])}

Please provide:
1. Is the weather suitable for {activity}?
2. What precautions should be taken?
3. What is the best time of day for this activity?
4. Any alternative suggestions if conditions aren't ideal?"""

    return types.GetPromptResult(
        description=f"Weather advice for {activity} in {city}",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=prompt_text
                )
            )
        ]
    )


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools that clients can call.

    Returns the tools exposed by this server for direct invocation.
    """
    return [
        types.Tool(
            name="get_weather",
            description="Get current weather information for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },
                "required": ["city"]
            }
        ),
        types.Tool(
            name="get_clothing_recommendation",
            description="Get clothing recommendations based on city weather",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },
                "required": ["city"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """
    Execute a tool call and return results.

    Handles direct tool invocations from clients, fetching weather data
    and providing clothing recommendations.

    Args:
        name: Name of the tool to execute
        arguments: Dictionary of tool arguments

    Returns:
        List of text content responses

    Raises:
        ValueError: If the tool name is unknown or arguments are invalid
    """
    if not arguments:
        raise ValueError("Missing arguments")

    city = arguments.get("city")
    if not city:
        raise ValueError("City name is required")

    try:
        latitude, longitude = await get_coordinates(city)
        weather = await get_weather(latitude, longitude)

        if name == "get_weather":
            result = {
                "city": city,
                "weather": weather
            }
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]

        elif name == "get_clothing_recommendation":
            clothing = recommend_clothing(weather)
            result = {
                "city": city,
                "weather": weather,
                "clothing_recommendation": clothing
            }
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        raise ValueError(f"Error processing request: {str(e)}")


async def main():
    """
    Start the MCP server.

    Runs the server using standard input/output for communication.
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-clothing-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
