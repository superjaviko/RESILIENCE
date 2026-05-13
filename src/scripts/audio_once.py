import bge

def position1(cont):
    own = cont.owner

    # Accede al sensor y los actuators
    near = cont.sensors['Near']
    sound1 = cont.actuators['Play1']  # Primer audio
    sound2 = cont.actuators['Play2']  # Segundo audio
    
    scene = bge.logic.getCurrentScene()
    obj = scene.objects.get("LoadingBarAI")
    
    if obj:
        obj.visible = True

    # Inicializa el contador si no existe
    if 'activaciones' not in own:
        own['activaciones'] = 0

    # Si el jugador está cerca y no se ha activado aún esta vez
    if near.positive and not own.get('ya_disparado', False):
        own['activaciones'] += 1  # Suma una activación
        own['ya_disparado'] = True  # Evita múltiples triggers seguidos

        if own['activaciones'] == 1:
            cont.activate(sound1)  # Reproduce el primer audio
            mostrar_flechas()
        elif own['activaciones'] == 3:
            cont.activate(sound2)  # Reproduce el segundo audio
            # Aquí puedes activar otra cosa si quieres

    # Reinicia el estado si el jugador se aleja
    if not near.positive:
        own['ya_disparado'] = False
    
def position2(cont):
    own = cont.owner

    # Accede al sensor y los actuators
    near = cont.sensors['Near']
    sound1 = cont.actuators['Play3']  # Primer audio
    sound2 = cont.actuators['Play4']  # Segundo audio
    
    scene = bge.logic.getCurrentScene()
    obj = scene.objects.get("LoadingBarIA")
    
    if obj:
        obj.visible = True

    # Inicializa el contador si no existe
    if 'activaciones2' not in own:
        own['activaciones2'] = 0

    # Si el jugador está cerca y no se ha activado aún esta vez
    if near.positive and not own.get('ya_disparado', False):
        own['activaciones2'] += 1  # Suma una activación
        own['ya_disparado2'] = True  # Evita múltiples triggers seguidos

        if own['activaciones'] == 1:
            cont.activate(sound1)  # Reproduce el primer audio
            mostrar_flechas()
        elif own['activaciones'] == 2:
            cont.activate(sound2)  # Reproduce el segundo audio
            # Aquí puedes activar otra cosa si quieres

    # Reinicia el estado si el jugador se aleja
    if not near.positive:
        own['ya_disparado'] = False


def mostrar_flechas():
    scene = bge.logic.getCurrentScene()

    for i in range(32, 48):  # Flechas Arrow.032 a Arrow.047
        nombre = f"Arrow.{str(i).zfill(3)}"
        if nombre in scene.objects:
            flecha = scene.objects[nombre]
            flecha.visible = True
