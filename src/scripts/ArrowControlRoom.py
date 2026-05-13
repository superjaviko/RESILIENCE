import bge

def main(cont):
    scene = bge.logic.getCurrentScene()
    tiempo = int(bge.logic.getRealTime() * 2) 

    for i in range(32): 
        if i == 0:
            nombre = "Arrow"
        else:
            nombre = f"Arrow.{str(i).zfill(3)}"

        if nombre in scene.objects:
            obj = scene.objects[nombre]
            obj.visible = i <= tiempo
