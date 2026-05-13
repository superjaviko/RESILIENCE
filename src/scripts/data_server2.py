import bge
import socket
import json
import threading

HOST = '127.0.0.1'  # Server address
PORT = 5000  # Server port

def request_training_sessions(operator_id, callback):
    """Send a request to the external script asynchronously."""
    def network_task():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((HOST, PORT))
                request = json.dumps({"operator_id": operator_id})
                client.sendall(request.encode('utf-8'))
                
                response = client.recv(1024).decode('utf-8')
                training_sessions, _ = response.split(",")  # Extract training_sessions
                
                # Use bge.logic to update the game safely
                bge.logic.getCurrentScene().objects[callback]["Text"] = training_sessions
        except Exception as e:
            print(f"❌ Network Error: {e}")

    threading.Thread(target=network_task, daemon=True).start()

def request_assisted_training(operator_id, callback):
    """Send a request to the external script asynchronously."""
    def network_task():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((HOST, PORT))
                request = json.dumps({"operator_id": operator_id})
                client.sendall(request.encode('utf-8'))
                
                response = client.recv(1024).decode('utf-8')
                _, assisted_training = response.split(",")  # Extract assisted_training
                
                # Use bge.logic to update the game safely
                bge.logic.getCurrentScene().objects[callback]["Text"] = assisted_training
        except Exception as e:
            print(f"❌ Network Error: {e}")

    threading.Thread(target=network_task, daemon=True).start()

def update_training_info(cont):
    """UPBGE Logic Brick Function - Updates Training Sessions."""
    scene = bge.logic.getCurrentScene()
    
    input_text_obj = scene.objects.get("Utente")  # Player enters ID here
    output_text_obj = "Utente.002"  # Name of output text object

    if input_text_obj:
        entered_id = input_text_obj["Text"].strip()  # Get user input
        if entered_id:
            request_training_sessions(entered_id, output_text_obj)  # Run in background thread
    else:
        print("❌ Error: Input text object not found in scene.")

def update_assisted_training_info(cont):
    """UPBGE Logic Brick Function - Updates Assisted Training."""
    scene = bge.logic.getCurrentScene()
    
    input_text_obj = scene.objects.get("Utente")  # Player enters ID here
    output_text_obj = "Utente.004"  # Name of output text object

    if input_text_obj:
        entered_id = input_text_obj["Text"].strip()  # Get user input
        if entered_id:
            request_assisted_training(entered_id, output_text_obj)  # Run in background thread
    else:
        print("❌ Error: Input text object not found in scene.")
