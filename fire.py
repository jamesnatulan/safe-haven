# Contains functions for fetching fire data

import requests
from requests.exceptions import HTTPError, Timeout, RequestException
import streamlit as st
import csv
from io import StringIO

from utils import get_lat_lon


BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/"

def get_fire_data(api_key, location, radius=100, satellite="modis", days=7):
    """
    Fetches fire data for a given area and date range using the FIRMS API.
    
    Args:
        api_key (str): The API key for accessing the FIRMS API.
        location (tuple): The location for which to fetch fire data. In the format (latitude, longitude).
        radius (int): Radius in kilometers to search for fire data.
        
    Returns:
        dict: Fire data if successful, None otherwise.
    """
    # Build the url with the provided API key and parameters
    url = f"{BASE_URL} {api_key}/{satellite}/{location[0]},{location[1]},{radius}/{days}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text  # Return the response text directly as it is in CSV format

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
    except Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except RequestException as req_err:
        print(f"Request error: {req_err}")

    return None  # Return None if an error occurred


def get_fire_risk(openai_client, gmaps_client, address):
    """
    Returns the fire risk for a given address.
    
    Args:
        openai_client (OpenAI): The OpenAI client instance.
        gmaps_client (googlemaps.Client): The Google Maps client instance.
        address (str): The address for the model to assess for fire risk.
        
    Returns:
        str: A message indicating the fire risk level.
    """

    prompt = """
        You are an expert in fire risk assessment. Provided the data below, determine
        the fire risk level. Please provide a number between 1 and 10 where 1 is low risk and 10 
        is high risk. Also, give a brief explanation of the factors that contribute to the
        assessed risk level. Provide your response in the following format:
        Risk Level: <number> \n
        Explanation: <brief explanation> \n
    """

    lat_lon = get_lat_lon(gmaps_client, address)
    
    if not lat_lon:
        return "Could not determine location for the provided address."

    api_key = st.secrets["FIRMS_MAP_KEY"]
    fire_data = get_fire_data(api_key, lat_lon)

    recent_fire_data = ""
    if fire_data:
        reader = csv.DictReader(StringIO(fire_data))
        fires = list(reader)

        print(f"Fetched fire data: {fires}")  # Debugging line to check fetched data

        fires_list = []
        if fires:
            for sample in fires:
                fire = {
                    'latitude': sample['latitude'],
                    'longitude': sample['longitude'],
                    'brightness': sample['brightness'],
                    'scan_time': sample['scan_time'],
                    'acq_date': sample['acq_date'],
                    'acq_time': sample['acq_time'],
                    'confidence': sample['confidence']
                }

                fires_list.append(fire)

        recent_fire_data = "\n".join(
            f"Latitude: {fire['latitude']}, Longitude: {fire['longitude']}, "
            f"Brightness: {fire['brightness']} K, Scan Time: {fire['scan_time']}, "
            f"Acquisition Date: {fire['acq_date']}, Acquisition Time: {fire['acq_time']}, "
            f"Confidence: {fire['confidence']}%"
            for fire in fires_list
        )

        # Combine the prompt with the fire data
        location_info = f"Location: {lat_lon[0]}, {lat_lon[1]}"
        full_prompt = f"{prompt}\n\n{location_info}\n\nRecent Fire Data: {recent_fire_data}"

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
        