from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Makes a request to the NWS API."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"error": f"Request error: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

def format_alert(feature: dict) -> str:
    """Formats a weather alert."""
    props = feature.get("properties", {})
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool(description="Get weather alerts for a US state. Provide the state abbreviation (e.g., 'CA' for California).")
async def get_alerts(state: str) -> str:
    """Fetches weather alerts for a US state."""
    if len(state) != 2 or not state.isalpha():
        return "Invalid state format. Please provide a valid US state abbreviation (e.g., 'CA' for California)."

    url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return data.get("error", "Unable to fetch alerts or no alerts found.")

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool(description="Get the weather forecast for a location. Provide the location as 'latitude,longitude' (e.g., '52.0333,7.1167').")
async def get_forecast(location: str) -> str:
    """Fetches the weather forecast for a specific location."""
    try:
        latitude, longitude = map(float, location.split(","))
    except ValueError:
        return "Invalid location format. Please provide 'latitude,longitude'."

    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data or "properties" not in points_data:
        return points_data.get("error", "Unable to fetch forecast data for this location.")

    forecast_url = points_data["properties"].get("forecast")
    if not forecast_url:
        return "Forecast URL not found in the response."

    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data or "properties" not in forecast_data:
        return forecast_data.get("error", "Unable to fetch detailed forecast.")

    periods = forecast_data["properties"].get("periods", [])
    if not periods:
        return "No forecast data available."

    forecasts = []
    for period in periods[:5]:  # Show only the next 5 periods
        forecast = f"""
{period.get('name', 'Unknown')}:
Temperature: {period.get('temperature', 'N/A')}°{period.get('temperatureUnit', '')}
Wind: {period.get('windSpeed', 'N/A')} {period.get('windDirection', 'N/A')}
Forecast: {period.get('detailedForecast', 'No forecast available')}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

if __name__ == "__main__":
    # Start the MCP server
    mcp.run(transport="stdio")