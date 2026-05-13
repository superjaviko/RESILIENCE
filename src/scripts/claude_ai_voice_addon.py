bl_info = {
    "name": "Claude Voice Assistant",
    "author": "Ing. avier E. Suarez Savigne",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Claude AI",
    "description": "Talk to Claude AI and get a voice answer",
    "category": "3D View"
}

import bpy
import os
import tempfile
import speech_recognition as sr
import requests
import json
from gtts import gTTS
from pydub import AudioSegment
import aud

# ⛔ Usa una variable de entorno para tu API KEY (NO dejes tu clave en el código)
CLAUDE_API_KEY = "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"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
TEMP_DIR = tempfile.gettempdir()
MP3_PATH = os.path.join(TEMP_DIR, "respuesta.mp3")
WAV_PATH = os.path.join(TEMP_DIR, "respuesta.wav")


def grabar_voz():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Di tu pregunta...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        texto = r.recognize_google(audio, language="it-IT")
        print(f"✅ Pregunta reconocida: {texto}")
        return texto
    except Exception as e:
        print("❌ Error al reconocer voz:", e)
        return None


def preguntar_a_claude(texto):
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": texto}
        ]
    }

    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        mensaje = response.json()["content"][0]["text"]
        print("💬 Claude respondió:", mensaje)
        return mensaje
    except Exception as e:
        print("❌ Error con Claude:", e)
        return "Errore nel contattare Claude."


def texto_a_audio(texto, ruta_mp3, ruta_wav):
    tts = gTTS(text=texto, lang='it')
    tts.save(ruta_mp3)
    print(f"🔊 Audio MP3 guardado en: {ruta_mp3}")
    sound = AudioSegment.from_mp3(ruta_mp3)
    sound.export(ruta_wav, format="wav")
    print(f"✅ Convertido a WAV en: {ruta_wav}")


def reproducir_audio(ruta):
    device = aud.Device()
    sound = aud.Sound(ruta)
    handle = device.play(sound)
    handle.loop_count = 0
    print("▶️ Reproduciendo respuesta...")


class CLAUDE_OT_voz(bpy.types.Operator):
    bl_idname = "claude_ai.escuchar"
    bl_label = "Talk to Claude AI"

    def execute(self, context):
        if not CLAUDE_API_KEY:
            self.report({'ERROR'}, "❌ No se encontró CLAUDE_API_KEY en variables de entorno.")
            return {'CANCELLED'}

        pregunta = grabar_voz()
        if not pregunta:
            self.report({'ERROR'}, "No se pudo reconocer la voz.")
            return {'CANCELLED'}

        respuesta = preguntar_a_claude(pregunta)
        texto_a_audio(respuesta, MP3_PATH, WAV_PATH)
        reproducir_audio(WAV_PATH)

        self.report({'INFO'}, "Conversación completada.")
        return {'FINISHED'}


class CLAUDE_PT_panel(bpy.types.Panel):
    bl_label = "Claude Voice Assistant"
    bl_idname = "CLAUDE_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Claude AI'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Ask a voice question")
        layout.operator("claude_ai.escuchar", icon="SPEAKER")


classes = [CLAUDE_OT_voz, CLAUDE_PT_panel]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
