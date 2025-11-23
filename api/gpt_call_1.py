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

def get_outing_suggestion_gemini_schema(
    city, mood, purpose, time_of_day, weather, number_of_people,
    type_of_people, hours_available, budget
) -> OutingSuggestion:

    genai.configure(api_key="AIzaSyCKk3jAhH6P2Jx2csQVT8zR2FpTXXB0U5k")

    prompt = f"""
You are a cultural concierge for young travelers and families.

Your task is to suggest a short, realistic 2- or 3-stop outing plan. 
The outing should feel smooth, spontaneous, and enjoyable — like something they could actually do today.

Context:
- City: {city}
- Mood: {mood}
- Purpose: {purpose}
- Time of day: {time_of_day}
- Weather: {weather}
- Number of people: {number_of_people} ({type_of_people})
- Total time available: {hours_available} hours
- Budget: ₹{budget} per person

Instructions:
- If time is under 2.5 hours, suggest 2 stops, otherwise 3
- Suggest only categories/types of places, not specific names
- Avoid rare/uncommon place types
- Ensure all stops are logically connected (walkable or short drive)
- Follow an energy curve (e.g., calm → active → chill), adapt to mood/purpose
- Max travel per stop: 20 minutes by car
- **Output ONLY a valid JSON object** with key "stops" as a list of {"vibe_title", "search_phrase"} dictionaries
"""

    try:
        response = genai.generate_text(
            model="models/gemini-2.5-flash",
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=10000
        )

        raw_output = response.output_text.strip()

        # Extract JSON from the output
        json_string = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if json_string:
            output_json = json.loads(json_string.group(0))
            return OutingSuggestion(**output_json)
        else:
            print(f"No JSON found in model output: {raw_output}")
            return OutingSuggestion(stops=None)

    except Exception as e:
        print(f"Error generating outing suggestion: {e}")
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
