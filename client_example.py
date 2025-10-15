"""
MCP Client Example

This client demonstrates how to connect to the weather MCP server,
call its tools, and use its prompts. It shows the complete flow from
asking a question to getting structured weather and clothing advice.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic


async def run_mcp_client():
    """
    Connect to the MCP server and demonstrate its capabilities.

    This function shows how to:
    1. Connect to the weather MCP server
    2. Call tools to get weather and clothing data
    3. Use prompts to get structured advice
    """

    # Path to your server script
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the connection
            await session.initialize()

            print("=" * 70)
            print("MCP WEATHER CLIENT - DEMO")
            print("=" * 70)
            print()

            # Example 1: List available tools
            print("AVAILABLE TOOLS:")
            print("-" * 70)
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  • {tool.name}: {tool.description}")
            print()

            # Example 2: List available prompts
            print("AVAILABLE PROMPTS:")
            print("-" * 70)
            prompts = await session.list_prompts()
            for prompt in prompts.prompts:
                print(f"  • {prompt.name}: {prompt.description}")
                if prompt.arguments:
                    print("    Arguments:")
                    for arg in prompt.arguments:
                        required = "required" if arg.required else "optional"
                        print(f"      - {arg.name} ({required}): {arg.description}")
            print()

            # Example 3: Get weather for a city
            city = "Paris"
            print(f"🌤️  GETTING WEATHER FOR {city.upper()}:")
            print("-" * 70)

            weather_result = await session.call_tool(
                "get_weather",
                arguments={"city": city}
            )

            weather_data = json.loads(weather_result.content[0].text)
            print(json.dumps(weather_data, indent=2))
            print()

            # Example 4: Get clothing recommendation
            print(f"👕 GETTING CLOTHING RECOMMENDATION FOR {city.upper()}:")
            print("-" * 70)

            clothing_result = await session.call_tool(
                "get_clothing_recommendation",
                arguments={"city": city}
            )

            clothing_data = json.loads(clothing_result.content[0].text)
            print(json.dumps(clothing_data, indent=2))
            print()

            # Example 5: Use the prompt for activity advice
            activity = "hiking"
            print(f"🏔️  GETTING PROMPT FOR {activity.upper()} IN {city.upper()}:")
            print("-" * 70)

            prompt_result = await session.get_prompt(
                "weather_advice",
                arguments={"city": city, "activity": activity}
            )

            print(f"Prompt Description: {prompt_result.description}")
            print()
            print("Generated Prompt:")
            print("-" * 70)
            for message in prompt_result.messages:
                print(message.content.text)
            print()

            print("=" * 70)
            print("✅ DEMO COMPLETED")
            print("=" * 70)


async def run_with_ai_assistant():
    """
    Demonstrate the full flow: MCP server → Prompt → AI Assistant → Response

    This shows how an AI assistant (like Claude) would use the MCP server
    to answer a user's question about activities and weather.
    """

    print("\n" + "=" * 70)
    print("FULL AI ASSISTANT FLOW DEMO")
    print("=" * 70)
    print()

    # Initialize Anthropic client (requires ANTHROPIC_API_KEY environment variable)
    try:
        anthropic = Anthropic()
    except Exception as e:
        print("⚠️  Skipping AI demo: Set ANTHROPIC_API_KEY environment variable")
        print(f"   Error: {e}")
        return

    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # User asks a question
            user_question = "Should I go hiking in Tokyo today?"
            print(f"👤 USER QUESTION:")
            print(f"   '{user_question}'")
            print()

            # AI recognizes it needs weather data and requests prompt
            print("🤖 AI ASSISTANT: Fetching weather data via MCP...")
            print()

            prompt_result = await session.get_prompt(
                "weather_advice",
                arguments={"city": "Tokyo", "activity": "hiking"}
            )

            prompt_text = prompt_result.messages[0].content.text

            print("📤 STRUCTURED PROMPT SENT TO AI:")
            print("-" * 70)
            print(prompt_text)
            print()

            # Send to AI assistant
            print("🤖 AI ASSISTANT: Processing weather data and generating advice...")
            print()

            response = anthropic.messages.create(
                model="openai-4_mini",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt_text}
                ]
            )

            ai_response = response.content[0].text

            print("💬 AI ASSISTANT RESPONSE:")
            print("-" * 70)
            print(ai_response)
            print()

            print("=" * 70)
            print("✅ FULL FLOW COMPLETED")
            print("=" * 70)


async def main():
    """
    Run all demonstration examples.
    """
    # Run basic MCP client demo
    await run_mcp_client()

    # Run full AI assistant flow demo (optional, requires API key)
    await run_with_ai_assistant()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          MCP WEATHER & CLOTHING RECOMMENDATION CLIENT            ║
║                                                                  ║
║  This demo shows:                                                ║
║  1. How to connect to the MCP server                            ║
║  2. How to call tools (get_weather, get_clothing_recommendation)║
║  3. How to use prompts (weather_advice)                         ║
║  4. How AI assistants use the server to answer questions        ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())
