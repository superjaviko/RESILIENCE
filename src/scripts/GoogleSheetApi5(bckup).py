import bge
import gspread
import datetime  # Import datetime module
from oauth2client.service_account import ServiceAccountCredentials



# Define the scope and authenticate with the Google Sheets API
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    r'D:\PROJECTS\RESILIENCE\DOC\GOOGLE SHEET API\unical account\resilience-453416-5e2b2eae7608.json', scope)
client = gspread.authorize(creds)

# Open the correct Google Sheet by name
spreadsheet = client.open('RESILIENCE-DB')

# Select the correct worksheet
sheet = spreadsheet.worksheet('TrainingSessionKPI_UNICAL')

# Define object names and corresponding column mappings
object_mappings = {
    "Date": "Data",  # New field for current date
    "Ora": "Ora",  # New field for PC time
    "TrainingSessionID": "TrainingSession_ID",
    "Utente": "Operator_ID",
    "Procedure": "Procedure_ID",
    "CounterText": "Iteration_ID",
    "TempoAttuale": "Timestamp",  # This will be formatted as MM:SS
    "Knob1.003": "Assisted_Training",
    "Tempo": "CompletionTime",
    "TimeErrors": "TimeErrors",
    "Errori": "ProceduralErrors"
}

# Get the current scene
scene = bge.logic.getCurrentScene()

# Get current PC time and date
current_datetime = datetime.datetime.now()
current_date = current_datetime.strftime("%d-%m-%Y")  # Format as YYYY-MM-DD
current_time = current_datetime.strftime("%H:%M:%S")  # Format as HH:MM:SS

# Prepare data row for appending
data_row = []
for obj_name, column_name in object_mappings.items():
    if obj_name == "Date":
        prop_value = current_date  # Add current date
    elif obj_name == "Ora":
        prop_value = current_time  # Add real PC time
    else:
        obj = scene.objects.get(obj_name)
        if obj:
            if obj_name == "Utente":
                prop_value = obj.get("Text", "N/A")  # Get "text" property
            elif obj_name == "Tempo":
                raw_time = obj.get("time", 0)  # Get raw time value
                scaled_time = raw_time * 0.54  # Scale to real-time equivalent
                minutes = int(scaled_time // 60)
                seconds = int(scaled_time % 60)
                prop_value = f"{minutes}:{seconds:02d}"  # Format as MM:SS
            elif obj_name == "Errori":
                prop_value = obj.get("Text", "N/A")
            elif obj_name == "Knob1.003":
                prop_value = obj.get("TrainingGuidato", "N/A")
            elif obj_name == "CounterText":
                prop_value = obj.get("Text", "N/A")
            elif obj_name == "Procedure":
                prop_value = obj.get("Text", "N/A")
            else:
                prop_value = next(iter(obj.getPropertyNames()), "N/A")
        else:
            print(f"⚠️ Warning: Object '{obj_name}' not found in the scene.")
            prop_value = "N/A"  # Prevent breaking row format

    data_row.append(prop_value)

# Ensure the row isn't entirely "N/A" before appending
if all(value == "N/A" for value in data_row):
    print("⚠️ No valid data found. Skipping append.")
else:
    # Append data to Google Sheet
    sheet.append_row(data_row, value_input_option="USER_ENTERED")
    print("✅ Data appended successfully!")
