from gpt_call_1 import OutingSuggestion, get_outing_suggestion_gemini_schema
from map_call import text_search_places
from current_location import get_approximate_location_from_ip
from weather import get_weather_condition

API_KEY = "AIzaSyD71vUXnxhniEodZmfGxfbEIiDTexyKCjc"
WEATHER_API_KEY = "b0f411cd84d24d57bf170954251104"

import math

def haversine(lat1, lon1, lat2, lon2, earth_radius=6371):
  """
  Calculate the great circle distance between two points on the earth
  (specified in decimal degrees).

  Args:
    lat1 (float): Latitude of the first point.
    lon1 (float): Longitude of the first point.
    lat2 (float): Latitude of the second point.
    lon2 (float): Longitude of the second point.
    earth_radius (float, optional): Radius of the Earth in kilometers. Defaults to 6371.

  Returns:
    float: Distance between the two points in kilometers.
  """
  # Convert decimal degrees to radians
  lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

  # Differences in coordinates
  dlat = lat2 - lat1
  dlon = lon2 - lon1

  # Haversine formula
  a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  distance = earth_radius * c

  return distance

def create_weather_text(weather_conditions):
  """
  Generates a text description of the weather based on the provided conditions.

  Args:
    weather_conditions: A dictionary containing boolean values for 'is_raining'
                        and 'is_too_sunny'.

  Returns:
    A string describing the weather.
  """
  if weather_conditions['is_raining'] and weather_conditions['is_too_sunny']:
    return "It is raining even though it is too sunny."
  elif weather_conditions['is_raining']:
    return "It is currently raining."
  elif weather_conditions['is_too_sunny']:
    return "It is too sunny right now."
  else:
    return "The weather conditions are normal."
  
def find_best_places(places, top_n=4):
    """
    Ranks places based on a weighted combination of rating and review count.

    Args:
        places (list): A list of dictionaries, where each dictionary represents a place
                       and contains 'name', 'rating', and 'review_count' keys.
        top_n (int): The number of top places to return.

    Returns:
        list: A list of the top_n places, sorted by the ranking score in descending order.
    """
    if not places:
        return []

    ranked_places = []
    for place in places:
        rating = place.get('rating', 0.0)
        review_count = place.get('review_count', 0)

        # Simple weighted score: (normalized rating) * weight_rating + (normalized review_count) * weight_reviews
        # Normalizing helps to put both metrics on a similar scale (0 to 1)
        max_rating = 5.0  # Assuming max rating is 5
        max_review_count = max(p.get('review_count', 0) for p in places) if places else 1 # Avoid division by zero

        normalized_rating = rating / max_rating if max_rating > 0 else 0
        normalized_review_count = review_count / max_review_count if max_review_count > 0 else 0

        # You can adjust these weights based on how much importance you give to each factor
        weight_rating = 0.7
        weight_reviews = 0.3

        score = (normalized_rating * weight_rating) + (normalized_review_count * weight_reviews)
        ranked_place = place.copy()  # Start with a copy of the 'place' dictionary
        ranked_place['score'] = score  # Add the 'score'
        ranked_places.append(ranked_place)

    # Sort places by the calculated score in descending order
    ranked_places.sort(key=lambda item: item['score'], reverse=True)

    return ranked_places[:top_n]

def find_best_itinerary_multiple_categories(categories):
    """
    Finds the best set of places (one from each category) based on the total
    distance between them and their average rating. Prioritizes shorter total
    distance and higher average rating.

    Args:
        categories: A list of lists, where each inner list contains dictionaries
                    representing places in a category. Each place dictionary
                    should have 'Latitude', 'Longitude', and '⭐' keys.

    Returns:
        A tuple containing:
            - The best set of selected places (a list of dictionaries).
            - The total distance between these places.
            - The average rating of these places.
            Returns (None, float('inf'), -1) if no valid combination exists.
    """
    if not categories or any(not cat for cat in categories):
        return None, float('inf'), -1

    num_categories = len(categories)
    best_combination = None
    min_total_distance = float('inf')
    max_avg_rating = -1

    # Generate all possible combinations of one place from each category
    product_of_categories = [cat for cat in categories]
    combinations_list = list(zip(*product_of_categories))

    for combination in combinations_list:
        total_distance = 0
        avg_rating = sum(place['rating'] for place in combination) / num_categories

        # Calculate total distance by summing distances between consecutive places
        for i in range(num_categories):
            for j in range(i + 1, num_categories):
                place1 = combination[i]
                place2 = combination[j]
                distance = haversine(place1['latitude'], place1['longitude'],
                                               place2['latitude'], place2['longitude'])
                total_distance += distance

        # Prioritize shorter total distance, then higher average rating
        if total_distance < min_total_distance:
            min_total_distance = total_distance
            best_combination = list(combination)
            max_avg_rating = avg_rating
        elif total_distance == min_total_distance and avg_rating > max_avg_rating:
            min_total_distance = total_distance
            best_combination = list(combination)
            max_avg_rating = avg_rating

    return best_combination, min_total_distance, max_avg_rating

def generate_outing_suggestion(
    mood,
    purpose,
    time_of_day,
    number_of_people,
    type_of_people,
    hours_available,
    max_travel_time,
    transport_mode,
    budget,
    city=None,
    region=None,
    country=None,
    lat=None,
    lon=None,
    weather_conditions=None
):
    """
    Generate an outing suggestion based on the provided parameters.
    
    Args:
        mood (str): The current mood (e.g., "Relaxed and curious")
        purpose (str): The purpose of the outing (e.g., "Enjoy the evening")
        time_of_day (str): Time of day for the outing (e.g., "Evening")
        number_of_people (int): Number of people participating
        type_of_people (str): Type of people (e.g., "Adults")
        hours_available (float): Hours available for the outing
        max_travel_time (int): Maximum travel time in minutes
        transport_mode (str): Mode of transportation (e.g., "Car")
        budget (float): Available budget for the outing
        city (str, optional): City determined from IP
        region (str, optional): Region determined from IP
        country (str, optional): Country determined from IP
        lat (float, optional): Latitude determined from IP
        lon (float, optional): Longitude determined from IP
        weather_conditions (dict, optional): Weather conditions from API
    
    Returns:
        dict: An outing suggestion with stops and related information
    """
    # If location not provided, get it from IP
    if city is None or region is None or country is None or lat is None or lon is None:
        city, region, country, lat, lon = get_approximate_location_from_ip()
        print(f"Location details: {city}, {region}, {country}, {lat}, {lon}")
    
    # If weather conditions not provided, get them
    if weather_conditions is None:
        weather_conditions = get_weather_condition(lat, lon, WEATHER_API_KEY)
    
    # Create weather text
    weather = create_weather_text(weather_conditions=weather_conditions)

    # Get outing suggestion
    suggestion = get_outing_suggestion_gemini_schema(
        city, mood, purpose, time_of_day, weather, 
        number_of_people, type_of_people, hours_available, 
        max_travel_time, transport_mode, budget
    )

    results = {}
    if suggestion.stops:
        all_categories = []
        stops_info = []
        
        for i, stop in enumerate(suggestion.stops):
            stop_info = {
                "vibe_title": stop.vibe_title,
                "search_phrase": stop.search_phrase,
                "places": []
            }
            
            print(f"{i+1}. **{stop.vibe_title}** – _Search: \"{stop.search_phrase}\"_")
            place_results = text_search_places(
                stop.search_phrase, API_KEY, location=(lat, lon), max_results=5
            )
            final_results = find_best_places(place_results)
            
            for j, place in enumerate(final_results, 1):
                distance = haversine(lat, lon, place.get('latitude'), place.get('longitude'))
                
                place_info = {
                    "name": place['name'],
                    "rating": place['rating'],
                    "address": place['address'],
                    "place_id": place['place_id'],
                    "review_count": place['review_count'],
                    "latitude": place.get('latitude'),
                    "longitude": place.get('longitude'),
                    "distance": distance
                }
                
                stop_info["places"].append(place_info)
                
                print(f"{j}. {place['name']} ({place['rating']}⭐)")
                print(f"   Address: {place['address']}")
                print(f"   Place ID: {place['place_id']}")
                print(f"   Review count: {place['review_count']}")
                print(f"   Latitude: {place.get('latitude')}")
                print(f"   Longitude: {place.get('longitude')}")
                print(f"   Distance b/w locations: {distance} km")
            
            stops_info.append(stop_info)
            all_categories.append(final_results)
        
        best_combination, min_total_distance, max_avg_rating = find_best_itinerary_multiple_categories(all_categories)
        
        # results = {
        #     "suggestion": suggestion,
        #     "stops": stops_info,
        #     "best_itinerary": {
        #         "places": best_combination,
        #         "total_distance": min_total_distance,
        #         "average_rating": max_avg_rating
        #     }
        # }
        results = best_combination

        print(f"Results: {results}, {min_total_distance}, {max_avg_rating}")
    else:
        print("Could not generate outing suggestion in the expected format.")
        results = {"error": "Could not generate outing suggestion in the expected format."}
    

    print(f"Finallll resukts: {results}")
    return results