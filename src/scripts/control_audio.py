import bge

# Variable global para saber cuál audio está activo
audio_activo = None

def reproducir_audio(cont, nombre_actuador):
    global audio_activo

    own = cont.owner
    nuevo_audio = cont.actuators[nombre_actuador]

    # Si hay un audio activo y es distinto, lo detenemos
    if audio_activo and audio_activo != nuevo_audio:
        cont.deactivate(audio_activo)
        print("🛑 Deteniendo audio anterior")

    # Activamos el nuevo
    cont.activate(nuevo_audio)
    audio_activo = nuevo_audio
    print(f"🎧 Activando {nombre_actuador}")