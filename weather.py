# Contains functions for fetching weather data

import requests
from requests.exceptions import HTTPError, Timeout, RequestException
from utils import get_lat_lon

BASE_URL = "https://api.weather.gov"


def get_weather_data(user_agent, location):
    """
    Fetches weather data for a given location using the National Weather Service API.
    
    Args:
        location (tuple): The location for which to fetch the weather data. In the format (latitude, longitude).
        
    Returns:
        dict: Weather data if successful, None otherwise.
    """
    headers = {
        "User-Agent": user_agent,
    }

    try:
        endpoint = f"{BASE_URL}/points/{location[0]},{location[1]}"
        response = requests.get(
                       endpoint, 
                       headers=headers
                   )
        # Raise HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
        return response.json()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
    except Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except RequestException as req_err:
        print(f"Request error: {req_err}")
    
    return None  # Return None if an error occurred
    

def get_flood_risk(openai_client, gmaps_client, address):
    """
    Returns the flood risk for a given address.
    
    Args:
        openai_client (OpenAI): The OpenAI client instance.
        address (str): The address for the model to assess for flood risk.
        
    Returns:
        str: A message indicating the flood risk level.
    """
    system_prompt = """
    You are an expert in flood risk assessment. Provided the data below, determine
    the flood risk level. Please provide a number between 1 and 10 where 1 is low risk and 10 
    is high risk. Also, give a brief explanation of the factors that contribute to the
    assessed risk level. Make sure to be realistic and do not exaggerate the risk level.
    
    Provide your response in the following format:
    Risk Level: <number> \n
    Explanation: <brief explanation> \n
    """

    # Geocode the given address to get latitude and longitude
    lat, lon = get_lat_lon(gmaps_client, address)

    # Fetch weather data for the geocoded location
    weather_data = get_weather_data("FloodRiskAssessmentApp", (lat, lon))

    if weather_data:
        # Prepare the data for the OpenAI model
        forecast_url = weather_data.get("properties", {}).get("forecast", None)
        if forecast_url:
            try:
                forecast_response = requests.get(forecast_url)
                forecast_response.raise_for_status()
                forecast_data = forecast_response.json()
            except HTTPError as http_err:
                print(f"HTTP error occurred while fetching forecast: {http_err}")
                forecast_data = {"properties": {"forecast": "No forecast data available."}}
            except RequestException as req_err:
                print(f"Request error while fetching forecast: {req_err}")
                forecast_data = {"properties": {"forecast": "No forecast data available."}}

        location_info = f"Location: {lat}, {lon}"
        
        # Combine the prompt with the weather summary and location info
        user_prompt = f"{location_info}\n\nForecast Data: {forecast_data}"

        # Call the OpenAI model to get the flood risk assessment
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )

        # Extract and format the response
        if response and response.choices:
            response_content = response.choices[0].message.content.strip()

            if "Risk Level:" in response_content and "Explanation:" in response_content:
                risk_level = response_content.split("Risk Level:")[1].split("\n")[0].strip()
                explanation = response_content.split("Explanation:")[1].strip()
                return f"Risk Level: {risk_level}\nExplanation: {explanation}"
            
            else:
                return None
            
        else:
            return None