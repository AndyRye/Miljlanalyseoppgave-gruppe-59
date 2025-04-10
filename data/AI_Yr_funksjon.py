import os
import requests
from google import genai
from google.genai import types
from datetime import datetime, timedelta, timezone
from dateutil import parser
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

def get_geo_coordinates(city: str) -> Optional[dict]:
    """Get latitude and longitude for a city using Nominatim.

    Args:
        city: City name to geocode (e.g. "Oslo, Norway")

    Returns:
        Dictionary with 'lat' and 'lon' keys or None
    """
    url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
    headers = {'User-Agent': 'WeatherApp/1.0 (tvmoen@stud.ntnu.no)'}
    response = requests.get(url, headers=headers)
    if response.ok and response.json():
        data = response.json()[0]
        return {'lat': float(data['lat']), 'lon': float(data['lon'])}
    return None


def get_weather_forecast(lat: float, lon: float, start_date: str, end_date: str) -> Optional[list]:
    """Get weather forecast for coordinates from MET Norway API.

    Args:
        lat: Latitude
        lon: Longitude
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of forecast entries between dates
    """
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/complete?lat={lat}&lon={lon}"
    headers = {
        'User-Agent': 'WeatherApp/1.0 (tvmoen@stud.ntnu.no)',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        return None

    data = response.json()
    forecasts = []
    start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(end_date).replace(
        tzinfo=timezone.utc) + timedelta(days=1)

    for entry in data['properties']['timeseries']:
        entry_time = parser.parse(entry['time'])
        if start <= entry_time < end:
            forecasts.append({
                'time': entry['time'],
                'temperature': entry['data']['instant']['details']['air_temperature'],
                'precipitation': entry['data'].get('next_1_hours', {}).get('details', {}).get('precipitation_amount', 0),
                'humidity': entry['data']['instant']['details']['relative_humidity'],
                'wind_speed': entry['data']['instant']['details']['wind_speed']
            })

    return forecasts


config = types.GenerateContentConfig(
    tools=[get_geo_coordinates, get_weather_forecast]
)

api_key = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key=api_key)


input = input("Enter your weather query: ")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=config,
    contents=f"""
        You are a weather agent that provides weather forecasts for cities for the end user.

        you should present the data in a human-readable format, adding emojis as you see fit.

        If you don't understand the question, don't ask following questions, just assume what the user meant.

        When the user ask where it is the best weather. Prioritiez the high temperature, then sun, and low wind. Use all the data you are given and select the best place in Norway.

        If the user doesnt give you a spesific date. asssume it is tomorrow
        Todays date is {datetime.now().isoformat()}

        

        Query: {input}
    """
)

print(response.text)

