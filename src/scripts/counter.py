import bge
import os

# Nombre del archivo donde guardaremos el contador
counter_file = bge.logic.expandPath(r'D:\PROJECTS\RESILIENCE\DEVELOPMENT\VR\Runtime\Runtime\level\counter.txt')

def load_counter():
    """Carga el contador desde el archivo y lo asigna al objeto de texto."""
    scene = bge.logic.getCurrentScene()
    text_obj = scene.objects.get("CounterText")  # Asegúrate de que el nombre sea correcto

    if os.path.exists(counter_file):  # Si el archivo existe, leer el valor
        with open(counter_file, "r") as file:
            try:
                count = int(file.read().strip())  # Leer el número guardado
            except ValueError:
                count = 1  # Si hay error, iniciar en 1
    else:
        count = 1  # Si el archivo no existe, iniciar en 1

    text_obj["Text"] = str(count)  # Mostrar el contador en el juego
    return count

def save_counter(count):
    """Guarda el contador en el archivo."""
    with open(counter_file, "w") as file:
        file.write(str(count))

def update_counter():
    """Actualiza el contador, guarda el nuevo valor y lo muestra en el juego."""
    count = load_counter()  # Cargar el número actual
    count += 1  # Incrementar la sesión
    save_counter(count)  # Guardar el nuevo número
