import requests
import json

def get_weather_condition(latitude, longitude, api_key):
    """
    Calls the weatherapi.com API to get the current weather conditions
    and determines if it's raining and/or too sunny.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        api_key (str): Your weatherapi.com API key.

    Returns:
        dict: A dictionary containing boolean values for 'is_raining' and 'is_too_sunny'.
              Returns None if the API call fails.
    """
    url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={latitude},{longitude}&aqi=yes"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        weather_data = response.json()

        is_raining = False
        if 'precip_mm' in weather_data['current'] and weather_data['current']['precip_mm'] > 0:
            is_raining = True
        elif 'precip_in' in weather_data['current'] and weather_data['current']['precip_in'] > 0:
            is_raining = True

        is_too_sunny = False
        if weather_data['current']['is_day'] == 1:
            cloud_cover = weather_data['current'].get('cloud', 100)  # Default to 100 if not available
            uv_index = weather_data['current'].get('uv', 0)

            if weather_data['current']['condition']['text'].lower() == 'sunny' or \
               (cloud_cover < 30 and uv_index > 7):  # Consider low cloud cover and high UV as too sunny
                is_too_sunny = True
            elif 'heatindex_c' in weather_data['current'] and weather_data['current']['heatindex_c'] > 38: # Consider high heat index
                is_too_sunny = True
            elif 'feelslike_c' in weather_data['current'] and weather_data['current']['feelslike_c'] > 38: # Consider high feels-like temperature
                is_too_sunny = True


        return {
            'is_raining': is_raining,
            'is_too_sunny': is_too_sunny
        }

    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None
    except KeyError as e:
        print(f"Error accessing key in JSON: {e}")
        return None

# if __name__ == "__main__":
#     api_key = "b0f411cd84d24d57bf170954251104"  # Replace with your actual API key
#     latitude = 12.971581
#     longitude = 80.043419

#     weather_conditions = get_weather_condition(latitude, longitude, api_key)

#     if weather_conditions:
#         print(f"Is it raining? {weather_conditions['is_raining']}")
#         print(f"Is it too sunny? {weather_conditions['is_too_sunny']}")
#     else:
#         print("Could not retrieve weather information.")