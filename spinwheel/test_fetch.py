import gspread
import pandas as pd

GOOGLE_SHEETS_CREDENTIALS_FILE = 'spin-wheel-aon-robotis-07ae3d09ce09.json'
SPREADSHEET_NAME = 'Test'
WORKSHEET_NAME = 'Participants'

def fetch_data_from_google_sheet():
    try:
        gc = gspread.service_account(filename=GOOGLE_SHEETS_CREDENTIALS_FILE)
        spreadsheet = gc.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        data = worksheet.get_all_records()
        
        df = pd.DataFrame(data)
        df = df[['Name', 'Tickets']]
        df['Tickets'] = pd.to_numeric(df['Tickets'], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# --- Test ---
if __name__ == '__main__':
    df = fetch_data_from_google_sheet()
    if df is not None:
        print("Fetched Data:")
        print(df)
    else:
        print("Failed to fetch data from Google Sheets.")
