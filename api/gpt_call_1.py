import os
import json
import google.generativeai as genai
from typing import List, Optional
from pydantic import BaseModel, field_validator, ValidationError

# --- Your Pydantic Models (Keep these for parsing the output) ---
class OutingStop(BaseModel):
    vibe_title: str
    search_phrase: str

class OutingSuggestion(BaseModel):
    stops: Optional[List[OutingStop]]

    @field_validator('stops')
    def check_number_of_stops(cls, v):
        if v is not None and not (len(v) == 2 or len(v) == 3):
            raise ValueError("Number of stops must be 2 or 3 if provided.")
        return v

# --- The Refactored Function ---
def get_outing_suggestion_gemini_schema(
    city: str, 
    mood: str, 
    purpose: str, 
    time_of_day: str, 
    weather: str, 
    number_of_people: int,
    type_of_people: str, 
    hours_available: float, 
    budget: str  # Changed to str to match your curl input "Moderate"
) -> OutingSuggestion:

    api_key = "AIzaSyCKk3jAhH6P2Jx2csQVT8zR2FpTXXB0U5k"
    # Fallback for local testing if env var not set
    # if not api_key:
    #     api_key = "AIza..." # Put your actual key here for testing
    
    genai.configure(api_key=api_key)

    # --- FIX START: Manually define schema to avoid "$ref" error ---
    # We explicitly define the structure here so the SDK doesn't have to 
    # guess how to serialize the nested Pydantic model.
    gemini_schema = {
        "type": "OBJECT",
        "properties": {
            "stops": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "vibe_title": {"type": "STRING"},
                        "search_phrase": {"type": "STRING"}
                    },
                    "required": ["vibe_title", "search_phrase"]
                }
            }
        },
        "required": ["stops"]
    }
    # --- FIX END ---

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "application/json",
            "response_schema": gemini_schema # Pass the dict, not the Pydantic class
        }
    )

    target_stops = 2 if hours_available < 2.5 else 3

    prompt = f"""
    You are a cultural concierge. Suggest a short, realistic {target_stops}-stop outing plan.
    
    Context:
    - City: {city}
    - Mood: {mood}
    - Purpose: {purpose}
    - Time: {time_of_day}
    - Weather: {weather}
    - Crowd: {number_of_people} ({type_of_people})
    - Time Available: {hours_available} hours
    - Budget: {budget}

    Constraints:
    - Suggest EXACTLY {target_stops} stops.
    - Suggest categories of places, not specific business names (e.g., "Art Cafe" not "Starbucks").
    - Avoid rare types.
    - Stops must be logically connected.
    """

    try:
        response = model.generate_content(prompt)
        
        # We still use Pydantic here to validate the result
        return OutingSuggestion.model_validate_json(response.text)

    except ValidationError as ve:
        print(f"Validation Error: {ve}")
        return OutingSuggestion(stops=None)
    except Exception as e:
        print(f"Error generating outing suggestion: {e}")
        return OutingSuggestion(stops=None)