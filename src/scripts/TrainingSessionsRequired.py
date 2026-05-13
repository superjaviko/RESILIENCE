import bge
import socket
import json

HOST = '127.0.0.1'  # Same as the external server
PORT = 5000  # Port to connect to

def request_training_sessions(operator_id):
    """Send a request to the external script and return the response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))
            request = json.dumps({"operator_id": operator_id})
            client.sendall(request.encode('utf-8'))
            
            response = client.recv(1024).decode('utf-8')
            return response
    except Exception as e:
        return f"Error: {e}"

def update_training_info(cont):
    """UPBGE Logic Brick Function"""
    scene = bge.logic.getCurrentScene()
    
    input_text_obj = scene.objects.get("Utente")  # Player enters ID here
    output_text_obj = scene.objects.get("Utente.002")  # Shows training sessions

    if input_text_obj and output_text_obj:
        entered_id = input_text_obj["Text"].strip()  # Get user input
        
        if entered_id:
            training_sessions = request_training_sessions(entered_id)
            output_text_obj["Text"] = f"{training_sessions}"  # Update text
    else:
        print("❌ Error: One or both text objects not found in scene.")
