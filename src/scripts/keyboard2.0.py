import bge, bpy

# Obtener la escena
scene = bge.logic.getCurrentScene()

number1 = scene.objects["number1"]
number2 = scene.objects["number2"]
number3 = scene.objects["number3"]
number4 = scene.objects["number4"]
number5 = scene.objects["number5"]
number6 = scene.objects["number6"]
number7 = scene.objects["number7"]
number8 = scene.objects["number8"]
number9 = scene.objects["number9"]

text_obj = scene.objects.get("Utente")  

def update_text():
    current_text = text_obj["Text"] 
    return current_text

def handle_number(sensor, number):
        if sensor.positive: 
        current_text = update_text()
        
        new_text = current_text + str(number)
        text_obj["Text"] = new_text  # update text


def check_collisions(cont):
   
    handle_number(number1.sensors["Collision"], 1)
    handle_number(number2.sensors["Collision"], 2)
    handle_number(number3.sensors["Collision"], 3)
    handle_number(number4.sensors["Collision"], 4)
    handle_number(number5.sensors["Collision"], 5)
    handle_number(number6.sensors["Collision"], 6)
    handle_number(number7.sensors["Collision"], 7)
    handle_number(number8.sensors["Collision"], 8)
    handle_number(number9.sensors["Collision"], 9)


def main():
    cont = bge.logic.getCurrentController()
    check_collisions(cont) 

