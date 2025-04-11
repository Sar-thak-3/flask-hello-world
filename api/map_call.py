import requests
import json

def get_place_details(place_id, api_key):
    """
    Retrieves details for a specific place using the Google Places API,
    including the total number of user ratings.

    Args:
        place_id (str): The unique identifier of the place.
        api_key (str): Your Google Maps Platform API key.

    Returns:
        int or None: The total number of user ratings for the place,
                     or None if the request fails or the data is not found.
    """
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "user_ratings_total",
        "key": api_key
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()

        if data.get("status") == "OK" and "result" in data and "user_ratings_total" in data["result"]:
            return data["result"]["user_ratings_total"]
        else:
            print(f"Error retrieving place details: {data.get('status') or 'Unknown error'}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None

def text_search_places(query, api_key, location=None, radius=5000, max_results=5):
    """
    Perform a Google Places Text Search and return results.

    Args:
        query (str): The search query (e.g., 'coffee shops').
        api_key (str): Your Google Maps API key.
        location (tuple): Optional. Latitude and longitude as (lat, lng).
        radius (int): Optional. Search radius in meters. Default is 5000m.

    Returns:
        list: A list of dictionaries with name, address, rating, and place_id.
    """
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key,
    }

    if location:
        params["location"] = f"{location[0]},{location[1]}"
        params["radius"] = radius

    response = requests.get(base_url, params=params)
    data = response.json()

    if data.get("status") != "OK":
        print("API Error:", data.get("status"), data.get("error_message"))
        return []

    results = []
    for place in data.get("results", [])[:max_results]:
        # print(f"Place: {place}")
        # review_count = get_place_details(place.get("place_id"), api_key)
        results.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating"),
            "place_id": place.get("place_id"),
            "review_count": place.get("user_ratings_total"),
            "latitude": place.get("geometry").get("location").get("lat"),
            "longitude": place.get("geometry").get("location").get("lng")
        })

    return results

# API_KEY = "AIzaSyD71vUXnxhniEodZmfGxfbEIiDTexyKCjc"

# # Search with location (e.g., for 'pizza' near NYC)
# results = text_search_places("bowling alleys near me Andheri West", API_KEY, location=(13.0878, 80.2785))

# # Search without location
# # results = text_search_places("Eiffel Tower", API_KEY)

# for i, place in enumerate(results, 1):
#     print(f"{i}. {place['name']} ({place['rating']}⭐)")
#     print(f"   Address: {place['address']}")
#     print(f"   Place ID: {place['place_id']}\n")
#     print(f"   Review count: {place['review_count']}")
