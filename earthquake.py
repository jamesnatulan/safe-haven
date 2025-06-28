# Contains functions for fetching earthquake data

import requests
from requests.exceptions import HTTPError, Timeout, RequestException

from utils import get_lat_lon

BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def get_earthquake_data(location, radius=100):
    """
    Fetches earthquake data for a given location within a specified radius.
    
    Args:
        user_agent (str): User agent string for the request.
        location (tuple): The location for which to fetch earthquake data. In the format (latitude, longitude).
        radius (int): Radius in kilometers to search for earthquakes.
        
    Returns:
        dict: Earthquake data if successful, None otherwise.
    """

    # Get the time range for the last 60 days
    from datetime import datetime, timedelta
    endtime = datetime.now()
    starttime = endtime - timedelta(days=60)

    params = {
        'format': 'geojson',
        'latitude': location[0],
        'longitude': location[1],
        'maxradiuskm': radius,
        'starttime': starttime,
        'endtime': endtime
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
    except Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except RequestException as req_err:
        print(f"Request error: {req_err}")

    return None  # Return None if an error occurred


def get_earthquake_risk(openai_client, gmaps_client, address):
    """
    Returns the earthquake risk for a given address.
    
    Args:
        openai_client (OpenAI): The OpenAI client instance.
        gmaps_client (googlemaps.Client): The Google Maps client instance.
        address (str): The address for the model to assess for earthquake risk.
        
    Returns:
        str: A message indicating the earthquake risk level.
    """

    prompt = """
        You are an expert in earthquake risk assessment. Provided the data below, determine
        the earthquake risk level. Please provide a number between 1 and 10 where 1 is low risk and 10 
        is high risk. Also, give a brief explanation of the factors that contribute to the
        assessed risk level. Provide your response in the following format:
        Risk Level: <number> \n
        Explanation: <brief explanation> \n
    """

    lat_lon = get_lat_lon(gmaps_client, address)
    if not lat_lon:
        return "Could not determine location for the provided address."

    earthquake_data = get_earthquake_data(lat_lon)

    if earthquake_data:
        recent_earthquake_data = ""
        if 'features' not in earthquake_data or not earthquake_data['features']:
            recent_earthquake_data = "No recent earthquakes found in the vicinity."

        if earthquake_data['features']:
            earthquakes_list = []

            for feature in earthquake_data['features']:
                earthquake = {}
                
                earthquake['magnitude'] = feature['properties'].get('mag', 'N/A')
                earthquake['place'] = feature['properties'].get('place', 'Unknown location')
                earthquake['time'] = feature['properties'].get('time', 'Unknown time')

                earthquakes_list.append(earthquake)

            recent_earthquake_data = "\n".join(
                f"Magnitude: {eq['magnitude']}, Place: {eq['place']}, Time: {eq['time']}"
                for eq in earthquakes_list
            )    

        # Combine the prompt with the earthquake data
        location_info = f"Location: {lat_lon[0]}, {lat_lon[1]}"
        full_prompt = f"{prompt}\n\n{location_info}\n\nRecent Earthquake Data: {recent_earthquake_data}"

        # Call the OpenAI model to get the earthquake risk assessment
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
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