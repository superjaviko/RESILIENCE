import bge
import os

def main(cont):
    own = cont.owner
    ruta = bge.logic.expandPath(r"D:\PROJECTS\RESILIENCE\DEVELOPMENT\VR\RESILIENCE VR (AUDIO)\Runtime\level\comando.txt")

    # Solo ejecutar si no se ha hecho ya
    if not own.get('si_activado', False):
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                comando = f.read().strip().lower()

            if "si" in comando :
                cont.activate(cont.actuators['AudioSi'])  # activa el sonido
                own['si_activado'] = True

                # Borra el archivo para evitar repeticiones
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write("")