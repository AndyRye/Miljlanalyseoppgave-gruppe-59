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

def run_weather_query():
    """Main function to handle weather queries recursively"""

    # Configure Gemini AI with tool functions
    config = types.GenerateContentConfig(
        tools = [get_geo_coordinates, get_weather_forecast]
    )

    #set up Gemini client
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return
    
    client = genai.Client(api_key = api_key)

    # Conversation history to maintain context
    conversation_history = []

    #Run the query loop

    while True:
        #Get user input
        user_input = input("\nEnter your weather query (or 'exit' to quit): ")

        #Check if user wants to exit
        if user_input.lower() in ['exit','quit','q']:
            print("Thank you for using the Weather assistant. Goodbye!")
            break

        # Add user query to conversation history
        conversation_history.append(f"User: {user_input}")

        # Create prompt with conversation context
        current_date = datetime.now().isoformat()
        prompt = f"""

            You are a weather agent thatprovides weather forcasts for cities for the end user.

            You should present the data in a human-readable format, adding emojis as you see fit.

            Today's date is {current_date}

            If they ask you what the weather is today, give them only for today

            Previous conversation:
            {' '.join(conversation_history[-5:]) if len(conversation_history) > 1 else 'No previous conversations. '}

            Current query: {user_input}
            """
        
        try:
            #Generate response using Gemini
            response = client.models.generate_content(
                model = "gemini-2.0-flash",
                config = config,
                contents = prompt
            )

            # Display the response
            print("\nWeather Assistant:", response.text)

            # Add assistant response to conversation history
            conversation_history.append(f"Assistant: {response.text}")

        except Exception as e:
            print(f"\nError occurred:{str(e)}")
            print("Please try again with a different query.")

if __name__ == "__main__":
        print("Welcome to the Weather Assistant!")
        print("You can ask questions about weather in any city.")
        print("Type 'exit' at any time to quit.")
        run_weather_query()





    

      

        

















