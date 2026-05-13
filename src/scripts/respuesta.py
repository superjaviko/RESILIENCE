import bge
import aud
import os

def main(cont):
    own = cont.owner
    ruta = bge.logic.expandPath("//respuesta.wav")

    # Asegurarse de que no se reproduzca más de una vez
    if not own.get("respuesta_reproducida", False):
        if os.path.exists(ruta):
            device = aud.device()
            sonido = aud.Factory(ruta)
            device.play(sonido)
            print("🔊 Reproduciendo respuesta.wav")
            own["respuesta_reproducida"] = True