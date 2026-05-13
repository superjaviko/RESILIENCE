import bge

def send_game_over():
    cont = bge.logic.getCurrentController()
    # Enviar mensaje al objeto con nombre "GameOverPlane"
    bge.logic.sendMessage("show", "", "GameOverPlane")

scene = bge.logic.getCurrentScene()
ob = scene.objects

sensor = ob['CubeForSensorTimer']
timerText = ob['Tempo']
allarmTimer = ob['AllarmTimer']

# Set time scale for a more realistic timer speed
time_scale = 0.016  # Aproximadamente 60 fps

if sensor['TimerStart'] and not timerText['pause']:
    if not timerText['counting']:
        print('Reinicio')
        timerText['counting'] = True
        allarmTimer['counting'] = True
        timerText['time'] = timerText['actualValue']
        allarmTimer['actualValue'] = 65 # 2 minutos en segundos
    else:
        timerText['actualValue'] += time_scale
        allarmTimer['actualValue'] -= time_scale  # Cuenta regresiva
        
        #Activate the animation when then allarm is a 60 secs
        if 59.98 < allarmTimer['actualValue'] < 60.02:
             if not allarmTimer.get("animation_triggered"):
                anim_obj = ob.get("cameraFade")
                if anim_obj:
                    anim_obj.playAction("Shader NodetreeAction", 1, 5, layer=0, play_mode=bge.logic.KX_ACTION_MODE_PLAY)
                    anim_obj.playAction("Shader NodetreeAction", 5, 1, layer=0, play_mode=bge.logic.KX_ACTION_MODE_PLAY)
                    
                # Marcar como activado para que no se repita
                #allarmTimer["animation_triggered"] = True
                 
        # Cuando llega a cero, mandar el mensaje
        if allarmTimer['actualValue'] <= 0:
            allarmTimer['actualValue'] = 0
            if not allarmTimer.get("sent"):  # Solo una vez
                send_game_over()
                allarmTimer["sent"] = True

    # Formatear texto para mostrar en pantalla
    minutes_text = int(timerText['actualValue'] // 60)
    seconds_text = int(timerText['actualValue'] % 60)

    minutes_alarm = int(allarmTimer['actualValue'] // 60)
    seconds_alarm = int(allarmTimer['actualValue'] % 60)

    timerText['Text'] = "{}:{:02}".format(minutes_text, seconds_text)
    allarmTimer['Text'] = "{}:{:02}".format(minutes_alarm, seconds_alarm)

# Pausar
if timerText['pause']:
    if timerText['counting']:
        timerText['counting'] = False

# Reiniciar
if timerText['restart']:
    timerText['actualValue'] = 0
    timerText['time'] = 0
    timerText['restart'] = False
    timerText['Text'] = "0:00"
    allarmTimer['actualValue'] = 120
    allarmTimer['Text'] = "3:00"
    allarmTimer['sent'] = False
