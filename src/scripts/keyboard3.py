import bge

# Obtener la escena y los objetos
scene = bge.logic.getCurrentScene()

numbers = {
    1: scene.objects["number1"],
    2: scene.objects["number2"],
    3: scene.objects["number3"],
    4: scene.objects["number4"],
    5: scene.objects["number5"],
    6: scene.objects["number6"],
    7: scene.objects["number7"],
    8: scene.objects["number8"],
    9: scene.objects["number9"]
}

text_obj = scene.objects.get("Utente")  

def update_text():
    """Devuelve el texto actual del objeto de texto."""
    return text_obj["Text"] if text_obj else ""

def handle_number(sensor, number):
    """Añade un número al texto si hay colisión."""
    if sensor.positive:
        current_text = update_text()

        # ✅ Si el texto aún es "ID", reemplazarlo con el primer número
        if current_text == "-":
            new_text = str(number)
        else:
            new_text = current_text + str(number)  # ✅ Concatenar los siguientes números
        
        text_obj["Text"] = new_text  # ✅ Actualizar el texto

def check_collisions():
    """Verifica colisiones en los números y actualiza el texto."""
    for num, obj in numbers.items():
        if "Collision" in obj.sensors:
            handle_number(obj.sensors["Collision"], num)

def main():
    """Función principal ejecutada en UPBGE."""
    check_collisions()

