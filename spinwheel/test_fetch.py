import gspread
import pandas as pd

GOOGLE_SHEETS_CREDENTIALS_FILE = 'bold-impulse-477421-e8-5654ea3ddd52.json'
SPREADSHEET_NAME = 'Tyler, The Creator Tickets Raffle (respuestas)'
WORKSHEET_NAME = 'Respuestas de formulario 1'

NAME_COL = 2      # Column B
TICKETS_COL = 4   # Column D

def fetch_data_from_google_sheet():
    try:
        gc = gspread.service_account(filename=GOOGLE_SHEETS_CREDENTIALS_FILE)
        spreadsheet = gc.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

        # Read columns directly (skip header row)
        names = worksheet.col_values(NAME_COL)[1:]
        tickets = worksheet.col_values(TICKETS_COL)[1:]

        # Build DataFrame safely
        df = pd.DataFrame({
            'Name': names,
            'Tickets': tickets
        })

        # Clean data
        df['Tickets'] = pd.to_numeric(df['Tickets'], errors='coerce').fillna(0).astype(int)
        df = df[df['Name'].str.strip() != ""]

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
