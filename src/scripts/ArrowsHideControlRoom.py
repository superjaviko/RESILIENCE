import bge

def hide_arrowsCR(cont):
    scene = bge.logic.getCurrentScene()
    for i in range(32):
        name = "Arrow" if i==0 else f"Arrow.{str(i).zfill(3)}"
        if name in scene.objects:
            arrow = scene.objects[name]
            arrow.visible = False
            
def hide_arrowsQM02(cont):
    scene = bge.logic.getCurrentScene()
    for i in range(32, 48):
        name = f"Arrow.{str(i).zfill(3)}"
        if name in scene.objects:
            arrow = scene.objects[name]
            arrow.visible = False
            
def hide_arrowsQM09(cont):
    scene = bge.logic.getCurrentScene()
    for i in range(48, 61):
        name = f"Arrow.{str(i).zfill(3)}"
        if name in scene.objects:
            arrow = scene.objects[name]
            arrow.visible = False

def hide_arrowsQC(cont):
    scene = bge.logic.getCurrentScene()
    for i in range(60, 121):
        name = f"Arrow.{str(i).zfill(3)}"
        if name in scene.objects:
            arrow = scene.objects[name]
            arrow.visible = False