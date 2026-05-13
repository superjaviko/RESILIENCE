import bge


scene = bge.logic.getCurrentScene()
obj = scene.objects['BaseButton.041']

    #obj.blenderObject['colorAttr'] = [1, 1, 1, 1]

    #obj.blenderObject.update_tag()
    
# Inicializar propiedades si no existen
if "colorButton" not in obj:
    obj["colorButton"] = 0
if "colorTimer" not in obj:
    obj["colorTimer"] = 0.0
if "blinkDuration" not in obj:
    obj["blinkDuration"] = 0.0  # Tiempo total de parpadeo

def set_color_with_emission(color, emission_strength=3):
    if obj.get("currentColor") != color:
        obj["currentColor"] = color
        obj.blenderObject['colorAttr'] = color
        obj.blenderObject.update_tag()

        if obj.blenderObject.active_material:
            mat = obj.blenderObject.active_material
            nodes = mat.node_tree.nodes

            emission_node = None
            for node in nodes:
                if node.type == 'EMISSION':
                    emission_node = node
                    break
            if not emission_node:
                emission_node = nodes.new(type='ShaderNodeEmission')

            emission_node.inputs[0].default_value = color
            emission_node.inputs[1].default_value = emission_strength

            output_node = None
            for node in nodes:
                if node.type == 'OUTPUT_MATERIAL':
                    output_node = node
                    break
            if output_node:
                mat.node_tree.links.new(emission_node.outputs[0], output_node.inputs[0])

def color1():
    set_color_with_emission([1, 1, 1, 1], emission_strength=3)

def color2():
    set_color_with_emission([0, 0, 0, 0], emission_strength=0)

def blink_white():
    # Tiempo acumulado del parpadeo
    obj["blinkDuration"] += bge.logic.getFrameTime()
    if obj["blinkDuration"] < 10.0:
        # Hacer blink
        obj["colorTimer"] += bge.logic.getFrameTime()
        if obj["colorTimer"] > 0.5:
            obj["colorTimer"] = 0
            if obj["colorButton"] == 0:
                obj["colorButton"] = 1
                color1()
            else:
                obj["colorButton"] = 0
                color2()
    else:
        # Después de 10 segundos, mantener blanco
        color1()


