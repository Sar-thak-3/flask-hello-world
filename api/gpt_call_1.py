import os
import google.generativeai as genai
from typing import List, Optional, Union
from pydantic import BaseModel, field_validator
import json
import re
from map_call import text_search_places

class OutingStop(BaseModel):
    vibe_title: str
    search_phrase: str

class OutingSuggestion(BaseModel):
    stops: Optional[Union[List[OutingStop], List[OutingStop]]]

    @field_validator('stops')
    def check_number_of_stops(cls, v):
        if v is not None and not (len(v) == 2 or len(v) == 3):
            raise ValueError("Number of stops must be 2 or 3 if provided.")
        return v

def get_outing_suggestion_gemini_schema(city, mood, purpose, time_of_day, weather, number_of_people, type_of_people, hours_available, max_travel_time, transport_mode, budget) -> OutingSuggestion:
    """
    Generates a 2 or 3-stop outing plan using the Gemini API and returns it as a Pydantic schema.

    Args:
        city (str): The city for the outing.
        mood (str): The desired mood of the outing.
        purpose (str): The purpose of the outing.
        time_of_day (str): The current time of day.
        weather (str): The current weather conditions.
        number_of_people (int): The number of people in the group.
        type_of_people (str): The type of people in the group (e.g., adults, family with young kids).
        hours_available (float): The total time available for the outing in hours.
        max_travel_time (int): The maximum travel time between stops in minutes.
        transport_mode (str): The mode of transportation (e.g., walking, car, bike).
        budget (int): The budget per person in INR.

    Returns:
        OutingSuggestion: A Pydantic model containing the outing suggestions.
    """
    genai.configure(api_key="AIzaSyCKk3jAhH6P2Jx2csQVT8zR2FpTXXB0U5k")
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
You are a cultural concierge for young travelers and families.

Your job is to suggest a short, realistic 2- or 3-stop outing plan based on the user's context. The outing should feel smooth, spontaneous, and enjoyable — like something they could actually do today.

Use the following context:

- City: {city}
- Mood: {mood}
- Purpose: {purpose}
- Time of day: {time_of_day}
- Weather: {weather}
- Number of people: {number_of_people} ({type_of_people})
- Total time available: {hours_available} hours
- Max travel per stop: {max_travel_time} minutes
- Mode of movement: {transport_mode} (e.g., walking, car, bike)
- Budget: ₹{budget} per person

---

**Instructions:**
- If time is short (under 2.5 hours), suggest **2 stops** instead of 3
- Suggest only **categories or types of places**, not specific names or areas
- Avoid place types that are rare or uncommon in the given city
- Ensure that all stops feel logically connected and could realistically exist **within a shared zone** (walkable or short drive)
- Reflect the energy curve in the order (e.g., calm → active → chill again), but adapt based on mood/purpose
- Return your response as a valid JSON object with a key "stops" which is a list of dictionaries.
- Each dictionary in the "stops" list should have two keys: "vibe_title" and "search_phrase".
"""

    response = model.generate_content(prompt)
    raw_output = response.text.strip()

    # Remove any surrounding text that might interfere with JSON parsing
    json_string = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if json_string:
        json_string = json_string.group(0)
        try:
            output_json = json.loads(json_string)
            return OutingSuggestion(**output_json)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw response (cleaned): {json_string}")
            return OutingSuggestion(stops=None)
        except Exception as e:
            print(f"Error creating Pydantic model: {e}")
            print(f"Raw response (cleaned): {json_string}")
            return OutingSuggestion(stops=None)
    else:
        print(f"Could not find JSON object in the response: {raw_output}")
        return OutingSuggestion(stops=None)

# if __name__ == '__main__':
#     city = "Chennai"
#     mood = "Relaxed and curious"
#     purpose = "Enjoy the evening"
#     time_of_day = "Evening"
#     weather = "Warm and breezy"
#     number_of_people = 2
#     type_of_people = "Adults"
#     hours_available = 2.8
#     max_travel_time = 20
#     transport_mode = "Car"
#     budget = 800

#     suggestion: OutingSuggestion = get_outing_suggestion_gemini_schema(city, mood, purpose, time_of_day, weather, number_of_people, type_of_people, hours_available, max_travel_time, transport_mode, budget)

#     if suggestion.stops:
#         for i, stop in enumerate(suggestion.stops):
#             print(f"{i+1}. **{stop.vibe_title}** – _Search: \"{stop.search_phrase}\"_")
#     else:
#         print("Could not generate outing suggestion in the expected format.")