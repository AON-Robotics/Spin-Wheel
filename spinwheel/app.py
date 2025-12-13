import pandas as pd
import random
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import gspread

# --- Configuration ---
GOOGLE_SHEETS_CREDENTIALS_FILE = 'bold-impulse-477421-e8-5654ea3ddd52.json'
SPREADSHEET_NAME = 'Tyler, The Creator Tickets Raffle (respuestas)'
WORKSHEET_NAME = 'Respuestas de formulario 1'

NAME_COL = 2        
TICKETS_COL = 4     

app = Flask(__name__)
CORS(app)

def fetch_data_from_google_sheet():
    """Fetches names and ticket counts safely from Google Sheets."""
    try:
        gc = gspread.service_account(filename=GOOGLE_SHEETS_CREDENTIALS_FILE)
        spreadsheet = gc.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

        # Read columns directly (skip header row)
        names = worksheet.col_values(NAME_COL)[1:]
        tickets = worksheet.col_values(TICKETS_COL)[1:]

        df = pd.DataFrame({
            "Nombre Completo": names,
            "Cantidad de taquillas compradas": tickets
        })

        # Clean data
        df["Cantidad de taquillas compradas"] = (
            pd.to_numeric(df["Cantidad de taquillas compradas"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        df = df[df["Nombre Completo"].str.strip() != ""]
        df = df[df["Cantidad de taquillas compradas"] > 0]

        return df.to_dict("records")

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

@app.route('/api/fetch', methods=['GET'])
def get_wheel_data():
    participants = fetch_data_from_google_sheet()

    if not participants:
        return jsonify({"error": "Could not fetch participant data."}), 500

    total_tickets = sum(p["Cantidad de taquillas compradas"] for p in participants)

    if total_tickets == 0:
        return jsonify({"error": "No tickets sold."}), 400

    start_angle = 0
    wheel_data = []

    for p in participants:
        proportion = p["Cantidad de taquillas compradas"] / total_tickets
        angle_degrees = proportion * 360

        wheel_data.append({
            "name": p["Nombre Completo"],
            "tickets": p["Cantidad de taquillas compradas"],
            "proportion": proportion,
            "start_angle": start_angle,
            "end_angle": start_angle + angle_degrees,
            "angle_degrees": angle_degrees
        })

        start_angle += angle_degrees

    return jsonify(wheel_data)

@app.route('/api/spin', methods=['GET'])
def spin_wheel():
    participants = fetch_data_from_google_sheet()

    if not participants:
        return jsonify({"error": "Could not fetch participant data."}), 500

    weighted_list = []
    for p in participants:
        weighted_list.extend(
            [p["Nombre Completo"]] * p["Cantidad de taquillas compradas"]
        )

    if not weighted_list:
        return jsonify({"error": "No tickets sold."}), 400

    winner_name = random.choice(weighted_list)
    return jsonify({"winner": winner_name})

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)