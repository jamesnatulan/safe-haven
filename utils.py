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