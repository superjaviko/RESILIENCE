import gspread
import threading
import json
import socket
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets API Setup
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    r'D:\PROJECTS\RESILIENCE\DOC\GOOGLE SHEET API\unical account\resilience-453416-5e2b2eae7608.json', scope)
client = gspread.authorize(creds)

spreadsheet = client.open('RESILIENCE-DB')
sheet = spreadsheet.worksheet('TrainingRequirements_UNISA')

# Simple Socket Server to Communicate with UPBGE
HOST = '127.0.0.1'  # Localhost
PORT = 5000  # Port to listen on

def fetch_training_data(operator_id):
    """Fetch training sessions and assisted training info from Google Sheets."""
    try:
        operator_ids = sheet.col_values(2)[1:]  # Columna 'Operator ID' (B), omitiendo encabezado
        training_sessions = sheet.col_values(4)[1:]  # Columna 'ReqNumOfTrainingSessions' (D), omitiendo encabezado
        assisted_training = sheet.col_values(6)[1:]  # Columna 'AssistedTraining' (F), omitiendo encabezado

        if operator_id in operator_ids:
            index = operator_ids.index(operator_id)  # Encuentra el índice del ID buscado
            return f"{training_sessions[index]},{assisted_training[index]}"
                   # Devuelve los datos en formato JSON
        else:
            return "Not found,Not found"
    except Exception as e:
        return f"Error: {e},Error: {e}"

def handle_client(conn):
    """Handles requests from UPBGE."""
    while True:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            break

        request = json.loads(data)
        operator_id = request.get("operator_id", "").strip()
        response = fetch_training_data(operator_id)
        
        conn.sendall(response.encode('utf-8'))

def start_server():
    """Starts the local server to listen for UPBGE requests."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"✅ Server running on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    start_server()

