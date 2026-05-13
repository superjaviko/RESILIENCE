import bge
import socket
import json

HOST = '127.0.0.1'  # Same as the external server
PORT = 5000  # Port to connect to

def request_assistedTraining(operator_id):
    """Send a request to the external script and return the response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))
            request = json.dumps({"operator_id": operator_id})
            client.sendall(request.encode('utf-8'))
            
            response = client.recv(1024).decode('utf-8')
            training_sessions, assisted_training = response.split(",")  
            
        return assisted_training
    except Exception as e:
        return f"Error: {e}"

def update_assistedTraining_info(cont):
    """UPBGE Logic Brick Function"""
    scene = bge.logic.getCurrentScene()
    
    input_text_obj = scene.objects.get("Utente")  # Player enters ID here
    output_text_obj = scene.objects.get("Utente.004")  # Shows training sessions

    if input_text_obj and output_text_obj:
        entered_id = input_text_obj["Text"].strip()  # Get user input
        
        if entered_id:
            assisted_training = request_assistedTraining(entered_id)
            output_text_obj["Text"] = f"{assisted_training}"  # Update text
    else:
        print("❌ Error: One or both text objects not found in scene.")
