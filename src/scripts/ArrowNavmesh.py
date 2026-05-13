import bpy

import bpy

for i in range(120):  # Cambia este número si tienes más flechas
    name = "Arrow" if i == 0 else f"Arrow.{str(i).zfill(3)}"
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        obj["Navmesh"] = 0.0  # Asigna una propiedad float llamada "Navmesh"