import requests
import json
import googlemaps

# Replace with your Google Maps API key
GOOGLE_MAPS_API_KEY = "AIzaSyD71vUXnxhniEodZmfGxfbEIiDTexyKCjc"

def get_approximate_location_from_ip():
    """Gets an approximate location based on the public IP address."""
    try:
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        city = data.get("city")
        region = data.get("region")
        country = data.get("country")
        latitude = float(data.get("loc").split(',')[0])
        longitude = float(data.get("loc").split(',')[-1])
        return city, region, country, latitude, longitude
    except requests.exceptions.RequestException as e:
        print(f"Error getting IP information: {e}")
        return None, None, None, None, None

def geocode_location(latitude, longitude):
    """Uses the Google Maps Geocoding API to get details from coordinates."""
    if not GOOGLE_MAPS_API_KEY:
        print("Please set your GOOGLE_MAPS_API_KEY.")
        return None

    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    try:
        reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude))
        return reverse_geocode_result
    except googlemaps.exceptions.ApiError as e:
        print(f"Error from Google Maps Geocoding API: {e}")
        return None

# if __name__ == "__main__":
#     city, region, country, lat, lon = get_approximate_location_from_ip()

#     if city and region and country:
#         print(f"Approximate location based on IP:")
#         print(f"City: {city}")
#         print(f"Region: {region}")
#         print(f"Country: {country}")
#     #     if lat and lon:
#     #         print(f"Latitude: {lat}")
#     #         print(f"Longitude: {lon}")
#     #         geocode_result = geocode_location(lat, lon)
#     #         if geocode_result:
#     #             print("\nDetails from Google Maps Geocoding API:")
#     #             print(json.dumps(geocode_result, indent=4))
#     # else:
#     #     print("Could not determine approximate location from IP.")