import bge
import gspread
import threading
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets API Credentials (Only load once)
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    r'D:\PROJECTS\RESILIENCE\DOC\GOOGLE SHEET API\unical account\resilience-453416-5e2b2eae7608.json', scope)
client = gspread.authorize(creds)

# Open Google Sheet & Read Data
spreadsheet = client.open('RESILIENCE-DB_TEST')
sheet = spreadsheet.worksheet('OperatorKnowledge_UNISA')

def fetch_training_sessions(operator_id, output_text_obj):
    """Fetch training sessions from Google Sheets in a separate thread."""
    try:
        operator_ids = sheet.col_values(2)[1:]  # Skip header
        training_sessions = sheet.col_values(9)[1:]  # Skip header

        if operator_id in operator_ids:
            index = operator_ids.index(operator_id)  # Find index of entered ID
            training_value = training_sessions[index]  # Get corresponding training sessions
            output_text_obj["Text"] = f"Training Sessions: {training_value}"  # Update text
            print(f"✅ Found {operator_id}: {training_value} training sessions.")
        else:
            output_text_obj["Text"] = "Operator not found!"
            print("⚠️ Operator ID not found!")

    except Exception as e:
        print(f"❌ Error fetching data: {e}")

def update_training_info(cont):
    """Function to be called from UPBGE logic bricks."""
    scene = bge.logic.getCurrentScene()
    
    # Get input and output text objects
    input_text_obj = scene.objects.get("Utente")  # Where player types ID
    output_text_obj = scene.objects.get("Utente.002")  # Where result appears

    if input_text_obj and output_text_obj:
        entered_id = input_text_obj["Text"].strip()  # Get player input
        
        if entered_id:
            # Run API request in a separate thread to prevent game freezing
            threading.Thread(target=fetch_training_sessions, args=(entered_id, output_text_obj)).start()
    else:
        print("❌ Error: One or both text objects not found in scene.")
