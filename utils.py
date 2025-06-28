# Contains utility functions that is shared across the application.

def get_lat_lon(gmaps_client, address):
    """
    Returns the corresponding latitude and longitude for a given address.
    Args:
        gmaps_client (googlemaps.Client): The Google Maps client instance.
        address (str): The address to geocode.
    Returns:
        tuple: A tuple containing the latitude and longitude of the address.
    """
    geocode_result = gmaps_client.geocode(address)

    if geocode_result:
        lat = geocode_result[0]['geometry']['location']['lat']
        lon = geocode_result[0]['geometry']['location']['lng']
        return (lat, lon)
    else:
        raise ValueError("Geocoding failed. Please check the address provided.")
    

def get_color_risk_level(value):
    """
    Returns a color based on the value.
    Args:
        value (int): The value to determine the color.
    Returns:
        str: A string representing the color.
    """
    if value < 3:
        return "green"
    elif value < 6:
        return "yellow"
    elif value < 8:
        return "orange"
    else:
        return "red"
    
def get_color_preparedness_score(score):
    """
    Returns a color based on the preparedness score.
    Args:
        score (float): The preparedness score to determine the color.
    Returns:
        str: A string representing the color.
    """
    if score >= 80:
        return "green"
    elif score >= 50:
        return "yellow"
    elif score >= 30:
        return "orange"
    else:
        return "red"
    
def colored_text(text, color):
    return f'<span style="color: {color}; font-weight: bold;">{text}</span>'