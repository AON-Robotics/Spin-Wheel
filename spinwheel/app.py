import pandas as pd
import random
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import gspread

# --- Configuration ---
GOOGLE_SHEETS_CREDENTIALS_FILE = 'spin-wheel-aon-robotis-07ae3d09ce09.json'
SPREADSHEET_NAME = 'Test'
WORKSHEET_NAME = 'Participants'

app = Flask(__name__)
CORS(app) # Enable CORS for frontend communication

def fetch_data_from_google_sheet():
    """Fetches names and ticket counts from the Google Sheet."""
    try:
        # Authenticate using the service account file
        gc = gspread.service_account(filename=GOOGLE_SHEETS_CREDENTIALS_FILE)
        spreadsheet = gc.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Get all records as a list of dictionaries
        data = worksheet.get_all_records()
        
        # Convert to a DataFrame for easy processing
        df = pd.DataFrame(data)
        
        # Ensure column names match your sheet ('Name' and 'Tickets')
        df = df[['Name', 'Tickets']]
        df['Tickets'] = pd.to_numeric(df['Tickets'], errors='coerce').fillna(0).astype(int)
        
        return df.to_dict('records')
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        # Return empty list on failure
        return []

@app.route('/api/fetch', methods=['GET'])
def get_wheel_data():
    """
    API endpoint to fetch data and calculate segment angles for the frontend.
    """
    participants = fetch_data_from_google_sheet()
    
    if not participants:
        return jsonify({"error": "Could not fetch participant data."}), 500

    total_tickets = sum(p['Tickets'] for p in participants)
    
    if total_tickets == 0:
        return jsonify({"error": "No tickets sold."}), 400

    # Calculate angle for each participant
    start_angle = 0
    wheel_data = []
    
    for p in participants:
        proportion = p['Tickets'] / total_tickets
        angle_degrees = proportion * 360
        
        wheel_data.append({
            "name": p['Name'],
            "tickets": p['Tickets'],
            "proportion": proportion,
            "start_angle": start_angle,
            "end_angle": start_angle + angle_degrees,
            "angle_degrees": angle_degrees
        })
        start_angle += angle_degrees

    return jsonify(wheel_data)

@app.route('/api/spin', methods=['GET'])
def spin_wheel():
    """
    API endpoint to select a winner based on ticket weighting.
    """
    participants = fetch_data_from_google_sheet()
    
    if not participants:
        return jsonify({"error": "Could not fetch participant data."}), 500

    # Create a weighted list for selection (one entry per ticket)
    weighted_list = []
    for p in participants:
        weighted_list.extend([p['Name']] * p['Tickets'])
        
    if not weighted_list:
        return jsonify({"error": "No tickets sold."}), 400
    
    # Randomly select a winner from the weighted list
    winner_name = random.choice(weighted_list)
    
    return jsonify({"winner": winner_name})

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # Run the server
    # Use '0.0.0.0' for external access if deploying
    app.run(debug=True, port=5000)