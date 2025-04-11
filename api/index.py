from flask import Flask, jsonify, request
import traceback
from cumulative import generate_outing_suggestion

app = Flask(__name__)

@app.route('/api/data', methods=['POST'])
def receive_data():
    """
    This endpoint handles POST requests to '/api/data'.
    It expects JSON data containing user preferences for outing suggestions
    and returns the generated outing suggestions.
    
    Expected JSON input:
    {
        "mood": string,
        "purpose": string,
        "time_of_day": string,
        "number_of_people": integer,
        "type_of_people": string,
        "hours_available": float,
        "max_travel_time": integer,
        "transport_mode": string,
        "budget": float,
        "city": string (optional),
        "region": string (optional),
        "country": string (optional),
        "lat": float (optional),
        "lon": float (optional),
        "weather_conditions": object (optional)
    }
    """
    try:
        # Get JSON data from request
        request_data = request.get_json()

        print(f"Request data: {request_data}")
        
        if not request_data:
            response = {
                'status': 'error',
                'message': 'No JSON data received in the request body.'
            }
            return jsonify(response), 400
        
        # Check if required fields are present
        required_fields = ['mood', 'purpose', 'time_of_day', 'number_of_people', 
                          'type_of_people', 'hours_available', 'max_travel_time', 
                          'transport_mode', 'budget']
        
        missing_fields = [field for field in required_fields if field not in request_data]
        
        if missing_fields:
            response = {
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }
            return jsonify(response), 400
            
        # Generate outing suggestion using the received parameters
        suggestions = generate_outing_suggestion(**request_data)

        print(f"Suggestions here: {suggestions}")
        
        # Return successful response with outing suggestions
        response = {
            'status': 'success',
            'message': 'Outing suggestions generated successfully!',
            'data': suggestions
        }

        print(f"final_response: {response}")
        
        return jsonify(response), 200
        
    except Exception as e:
        # Log the full exception for debugging
        traceback_str = traceback.format_exc()
        print(f"Error processing request: {str(e)}")
        print(traceback_str)
        
        # Return error response
        response = {
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }
        return jsonify(response), 500
if __name__ == '__main__':
    print("Flask application is running...")
    print("Outing suggestion API available at: http://localhost:5000/api/data")
    app.run(debug=True, host='0.0.0.0', port=5000)
