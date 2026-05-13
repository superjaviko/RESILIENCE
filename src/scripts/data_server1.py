# ServerThread.py
import bge  # Solo si vas a usarlo dentro de UPBGE
import gspread
import threading
import json
import socket
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True  # Muy importante: hilo en segundo plano
        self.HOST = '127.0.0.1'
        self.PORT = 5000

        # Autenticación con Google Sheets
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            bge.logic.expandPath("//resilience-453416-5e2b2eae7608.json"), scope)
        client = gspread.authorize(creds)

        spreadsheet = client.open('RESILIENCE-DB')
        self.sheet = spreadsheet.worksheet('TrainingRequirements_UNISA')

    def fetch_training_data(self, operator_id):
        try:
            operator_ids = self.sheet.col_values(2)[1:]
            training_sessions = self.sheet.col_values(4)[1:]
            assisted_training = self.sheet.col_values(6)[1:]

            if operator_id in operator_ids:
                index = operator_ids.index(operator_id)
                return f"{training_sessions[index]},{assisted_training[index]}"
            else:
                return "Not found,Not found"
        except Exception as e:
            return f"Error: {e},Error: {e}"

    def handle_client(self, conn):
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            request = json.loads(data)
            operator_id = request.get("operator_id", "").strip()
            response = self.fetch_training_data(operator_id)
            conn.sendall(response.encode('utf-8'))

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.HOST, self.PORT))
            server.listen()
            print(f"✅ Server running on {self.HOST}:{self.PORT}")
            while True:
                conn, addr = server.accept()
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()
