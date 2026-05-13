import bge

def send_game_over():
    cont = bge.logic.getCurrentController()
    bge.logic.sendMessage("show", "", "GameOverPlane")
    sound_actuator2 = cont.actuator.get("GameOver")
    if sound_actuator2:
        cont.activate(sound_actuator2)

# Obtener referencias
scene = bge.logic.getCurrentScene()
ob = scene.objects
cont = bge.logic.getCurrentController()
own = cont.owner

sensor = ob['CubeForSensorTimer']
timerText = ob['Tempo']
allarmTimer = ob['AllarmTimer']

#sound_actuator1 = cont.actuators["HurryUp"]
#sound_actuator2 = cont.actuators["GameOver"]

# Escala de tiempo
time_scale = 0.016  # ~60 FPS

# Si el temporizador debe iniciar
if sensor['TimerStart'] and not timerText['pause']:
    if not timerText['counting']:
        print('Reinicio')
        timerText['counting'] = True
        allarmTimer['counting'] = True
        timerText['time'] = timerText['actualValue']
        allarmTimer['actualValue'] = 80  # segundos
    else:
        # Actualización del temporizador
        timerText['actualValue'] += time_scale
        allarmTimer['actualValue'] -= time_scale

        # Reproducir animación al llegar a 60 segundos
        if 59.98 < allarmTimer['actualValue'] < 60.02:
            if not allarmTimer.get("animation_triggered"):
                allarmTimer["animation_triggered"] = True
                sound_actuator1 = cont.actuator.get("HurryUp")
                if sound_actuator1:
                     cont.activate(sound_actuator1)
                allarmTimer["anim_cycles"] = 0
                allarmTimer["anim_direction"] = "forward"
                allarmTimer["anim_timer"] = 0.5
                anim_obj = ob.get("cameraFade")
                if anim_obj:
                    anim_obj.playAction("Shader NodetreeAction", 1, 5, layer=0, play_mode=bge.logic.KX_ACTION_MODE_PLAY)

        # Control de ciclos de animación
        if allarmTimer.get("animation_triggered"):
            allarmTimer["anim_timer"] -= time_scale
            if allarmTimer["anim_timer"] <= 0:
                anim_obj = ob.get("cameraFade")
                if anim_obj:
                    if allarmTimer["anim_direction"] == "forward":
                        anim_obj.playAction("Shader NodetreeAction", 5, 1, layer=0, play_mode=bge.logic.KX_ACTION_MODE_PLAY)
                        allarmTimer["anim_direction"] = "backward"
                    else:
                        allarmTimer["anim_cycles"] += 1
                        if allarmTimer["anim_cycles"] < 3:
                            anim_obj.playAction("Shader NodetreeAction", 1, 5, layer=0, play_mode=bge.logic.KX_ACTION_MODE_PLAY)
                            allarmTimer["anim_direction"] = "forward"
                        else:
                            allarmTimer["animation_triggered"] = False
                            allarmTimer["anim_direction"] = ""
                            allarmTimer["anim_cycles"] = 0
                allarmTimer["anim_timer"] = 0.5

        # Verificar fin del tiempo
        if allarmTimer['actualValue'] <= 0:
            allarmTimer['actualValue'] = 0
            if not allarmTimer.get("sent"):
                send_game_over()
                allarmTimer["sent"] = True

# Mostrar texto actualizado SIEMPRE
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
    allarmTimer['Text'] = "2:00"
    allarmTimer['sent'] = False