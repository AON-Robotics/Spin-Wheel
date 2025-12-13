# 🎡 Activity Spin Wheel

An interactive **spin wheel web app** built with **Flask**, **JavaScript**, and **Google Sheets integration**.  
Designed for fair and fun random selections based on participant “tickets” (weighted chances).  
Used by AON Robotics for activity selection and random draws.

---

## 🚀 Features

- 🎯 Dynamic spin wheel rendered on an HTML `<canvas>`
- 🔄 Real-time data fetched from a **Google Sheet**
- 🧮 Weighted spins (more tickets = higher chance of winning)
- 🧍 Automatically removes winners from the wheel
- 🧾 Displays a running list of winners
- ♻️ “FETCH” button to refresh data from Google Sheets
- 🧹 “CLEAR” button to reset the winner list
- 🌈 Colorful visual interface and smooth animations

---

## 🗂️ Project Structure

```
project/
│
├── app.py # Flask backend server
├── spin-wheel-aon-robotis-07ae3d09ce09.json # Google Service Account credentials
│
├── templates/
│ └── index.html # Main frontend interface
│
├── static/
│ ├── styles.css # Styling for buttons, layout, and wheel
│ └── img/
│ └── AON_LOGO.png # Organization logo (optional)
│
└── README.md # You are here
```

### 🐍 Python 3.x
-Install dependencies:
    -pip install flask flask-cors gspread pandas

## 🧠 Google Cloud Setup

- 1. Go to Google Cloud Console

- 2. Enable the Google Sheets API.

- 3. Create a Service Account and download the JSON credentials file.

- 4. Rename it (or update the path in app.py):

    GOOGLE_SHEETS_CREDENTIALS_FILE = 'spin-wheel-aon-robotis-07ae3d09ce09.json'

## 📊 Google Sheet Format

The app expects a sheet like this:

Name	Tickets
Alice	3
Bob	5
Carol	2

**Name** → Participant’s name

**Tickets** → Number of entries (weighted chance)

Sheet and worksheet names are configured in app.py:

SPREADSHEET_NAME = 'Test'
WORKSHEET_NAME = 'Participants'

## 🖥️ Running the App

Start the Flask server:

python3 app.py

Then open your browser and visit:

http://127.0.0.1:5000/

## 🧠 How It Works

The frontend requests participant data via:

**GET /api/fetch**

→ Flask pulls the latest data from Google Sheets
→ Each participant’s wheel segment is calculated by ticket proportion

Clicking SPIN animates the wheel and randomly selects a winner
→ The winner’s name is added to the WINNERS list
→ That participant is removed from the wheel

Clicking FETCH refetches updated names from Google Sheets
→ Useful if new participants were added during runtime

Clicking CLEAR empties the winners list (resets display only)