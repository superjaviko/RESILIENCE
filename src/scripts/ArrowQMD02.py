import bge

def main(cont):
    scene = bge.logic.getCurrentScene()
    tiempo = int(bge.logic.getRealTime() * 2)  # Ajusta la velocidad de aparición

    for i in range(32, 48): 
        nombre = f"Arrow.{str(i).zfill(3)}"

        if nombre in scene.objects:
            obj = scene.objects[nombre]
            obj.visible = (i - 32) <= tiempo