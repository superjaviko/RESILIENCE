import bge

def numero(cont):
    own = cont.owner
    sensors = cont.sensors
    actuators = cont.actuators

    collision1 = sensors.get("Collision")
    collision2 = sensors.get("Collision.001")
    sonido = actuators.get("Sound")

    if not sonido or not collision1 or not collision2:
        print("❌ Revisa nombres de sensores o actuador 'Sound'")
        return

    if (collision1.positive or collision2.positive) and not own.get("activado", False):
        own["activado"] = True
        cont.activate(sonido)
        print("🔊 Audio reproducido correctamente")