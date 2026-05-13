import bge

def send_hide_messages():
    scene = bge.logic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    
    # Obtener el objeto base y su sensor de colisión
    base = scene.objects['Charging_socket']
    collision_sensor = cont.sensors["Collision"]  # Nombre del sensor en Logic Bricks

    if collision_sensor.positive:  # Si la colisión ocurre
        # Obtener el controlador y el actuador de mensaje
        message_actuator = cont.actuators["Message"]  # Nombre del actuador de mensaje en Logic Bricks

        # Lista de objetos a los que se enviará el mensaje
        objects_to_hide = [
            "chiamareManutentore",
            "HangUpCallMessage"
        ]
        
        for obj_name in objects_to_hide:
            message_actuator.subject = "hide"  # Mensaje que se enviará
            #message_actuator.body = "True"  # Opcional, si quieres enviar un valor
            #message_actuator.toProperty = obj_name  # Enviar al objeto específico
            
            cont.activate(message_actuator)  # Activar el actuador de mensaje
