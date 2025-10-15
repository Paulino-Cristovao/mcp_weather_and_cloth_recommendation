"""
Simple Test Script

A standalone script to test weather fetching and clothing recommendations
without needing the full MCP infrastructure. Use this to quickly verify
that the weather API and recommendation logic work correctly.
"""

import asyncio
import json
from weather_server import (
    get_coordinates,
    get_weather,
    recommend_clothing,
    get_weather_description
)


async def test_weather_and_clothing(city: str):
    """
    Test weather fetching and clothing recommendations for a city.

    Args:
        city: Name of the city to check
    """
    print("=" * 70)
    print(f"WEATHER AND CLOTHING TEST FOR: {city.upper()}")
    print("=" * 70)
    print()

    try:
        # Step 1: Get coordinates
        print("📍 Step 1: Getting coordinates...")
        latitude, longitude = await get_coordinates(city)
        print(f"   Coordinates: {latitude}°N, {longitude}°E")
        print()

        # Step 2: Fetch weather
        print("🌤️  Step 2: Fetching weather data...")
        weather = await get_weather(latitude, longitude)
        print(f"   Temperature: {weather['temperature']}°C")
        print(f"   Conditions: {weather['weather_description']}")
        print(f"   Wind Speed: {weather['wind_speed']} km/h")
        print(f"   Humidity: {weather['humidity']}%")
        print()

        # Step 3: Get clothing recommendations
        print("👕 Step 3: Generating clothing recommendations...")
        clothing = recommend_clothing(weather)

        print("\n   CLOTHING LAYERS:")
        for layer in clothing['layers']:
            print(f"     • {layer}")

        print("\n   ACCESSORIES:")
        for accessory in clothing['accessories']:
            print(f"     • {accessory}")

        print(f"\n   FOOTWEAR:")
        print(f"     • {clothing['footwear']}")

        print("\n   GENERAL ADVICE:")
        for advice in clothing['general_advice']:
            print(f"     • {advice}")

        print()
        print("=" * 70)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("=" * 70)


async def test_multiple_cities():
    """
    Test weather and clothing recommendations for multiple cities
    to show how recommendations vary by weather conditions.
    """
    cities = ["Paris", "Tokyo", "New York", "Sydney", "Moscow"]

    print("\n" + "=" * 70)
    print("TESTING MULTIPLE CITIES")
    print("=" * 70)
    print()

    for city in cities:
        await test_weather_and_clothing(city)
        print("\n")
        await asyncio.sleep(1)  # Be nice to the API


async def interactive_mode():
    """
    Interactive mode where users can input city names and get
    weather and clothing recommendations in real-time.
    """
    print("\n" + "=" * 70)
    print("INTERACTIVE MODE")
    print("=" * 70)
    print("Enter city names to get weather and clothing recommendations.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 70)
    print()

    while True:
        try:
            city = input("Enter city name: ").strip()

            if city.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break

            if not city:
                print("Please enter a valid city name.\n")
                continue

            await test_weather_and_clothing(city)
            print("\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}\n")


async def main():
    """
    Main function to run tests.
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              WEATHER & CLOTHING RECOMMENDATION TEST              ║
║                                                                  ║
║  This script tests the core functionality:                      ║
║  • Geocoding (city name → coordinates)                          ║
║  • Weather fetching (Open-Meteo API)                            ║
║  • Clothing recommendations (based on weather)                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Choose mode
    print("Choose test mode:")
    print("  1. Single city test (Paris)")
    print("  2. Multiple cities test")
    print("  3. Interactive mode")
    print()

    try:
        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            await test_weather_and_clothing("Paris")
        elif choice == "2":
            await test_multiple_cities()
        elif choice == "3":
            await interactive_mode()
        else:
            print("Invalid choice. Running default test for Paris...")
            await test_weather_and_clothing("Paris")

    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye! 👋")


if __name__ == "__main__":
    asyncio.run(main())
