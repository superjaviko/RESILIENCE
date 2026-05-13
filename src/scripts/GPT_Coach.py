# OpenAI Voice Coach Addon para UPBGE
# Funciona con GPT-3.5 (gratis) usando la API de OpenAI

bl_info = {
    "name": "OpenAI Voice Coach",
    "blender": (3, 6, 0),
    "category": "Game Engine",
    "author": "Javier E. Suarez Savigne",
    "description": "Asistente de voz usando OpenAI GPT + Procedura operativa"
}

import bpy
import os
import json
import requests
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import subprocess
import threading
import time

# === Configuración ===
PROCEDIMIENTO_PATH = os.path.join(os.path.dirname(__file__), "procedura.json")
AUDIO_TEMP_PATH = os.path.join(tempfile.gettempdir(), "risposta_coach.mp3")
esecuzione_attiva = True

# === Cargar procedimiento ===
def carica_procedura():
    try:
        with open(PROCEDIMIENTO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("❌ Errore nel caricamento della procedura:", e)
        return None

# === Construir contexto para ChatGPT ===
def costruisci_contesto(domanda, procedura):
    passi = "\n".join([
        f"Passaggio {p['paso']}: {p['titolo']} - {p['dettaglio']}"
        for p in procedura.get("procedura", [])
    ])
    return (
        "Sei un assistente esperto che guida l'operatore in tempo reale.\n"
        "L'operatore deve seguire una procedura per controllare un allarme.\n"
        "Rispondi solo sulla base di questa procedura:\n\n"
        f"{passi}\n\n"
        f"Domanda: {domanda}\n"
        "Ricorda: non inventare passaggi. Se un passaggio non è definito, di' che non è presente."
    )

# === Reconocimiento de voz ===
def registra_voce():
    r = sr.Recognizer()
    with sr.Microphone(device_index=2) as source:
        print("🎙️ Parla ora...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        testo = r.recognize_google(audio, language="it-IT")
        print(f"✅ Riconosciuto: {testo}")
        return testo
    except Exception as e:
        print("❌ Errore nel riconoscimento vocale:", e)
        return None

# === Comunicación con OpenAI GPT ===
def chiedi_a_gpt(texto):
    api_key = "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"
    if not api_key:
        print("⚠️ Variabile OPENAI_API_KEY mancante.")
        return "Chiave API non configurata."

    procedura = carica_procedura()
    if not procedura:
        return "Procedura non trovata."

    contesto = costruisci_contesto(texto, procedura)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Sei un assistente tecnico che segue la procedura."},
            {"role": "user", "content": contesto}
        ],
        "temperature": 0.2,
        "max_tokens": 300
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print("⚠️ Errore API:", response.status_code, response.text)
            return "Errore nella risposta."
    except Exception as e:
        print("❌ Errore nella richiesta OpenAI:", e)
        return "Errore tecnico."

# === Reproducir audio ===
def riproduci_audio(testo):
    tts = gTTS(text=testo, lang='it')
    tts.save(AUDIO_TEMP_PATH)
    wav_path = AUDIO_TEMP_PATH.replace(".mp3", ".wav")
    AudioSegment.from_mp3(AUDIO_TEMP_PATH).export(wav_path, format="wav")
    subprocess.call(["powershell", "-c", f"(New-Object Media.SoundPlayer '{wav_path}').PlaySync()"])

# === Lógica principal en bucle ===
def flusso_coach():
    global esecuzione_attiva
    while esecuzione_attiva:
        domanda = registra_voce()
        if not domanda:
            print("🔁 Nessuna domanda. Riprovo...")
            continue
        risposta = chiedi_a_gpt(domanda)
        print("💬 GPT ha risposto:", risposta)
        riproduci_audio(risposta)
        time.sleep(1)

# === Operadores y UI ===
class OpenAICoachOperator(bpy.types.Operator):
    bl_idname = "wm.openai_voice_coach"
    bl_label = "Start Voice Coach"

    def execute(self, context):
        global esecuzione_attiva
        esecuzione_attiva = True
        threading.Thread(target=flusso_coach).start()
        return {'FINISHED'}

class OpenAICoachStopOperator(bpy.types.Operator):
    bl_idname = "wm.openai_voice_coach_stop"
    bl_label = "Stop Voice Coach"

    def execute(self, context):
        global esecuzione_attiva
        esecuzione_attiva = False
        self.report({'INFO'}, "🛑 Voice Coach disattivato.")
        return {'FINISHED'}

class OpenAICoachPanel(bpy.types.Panel):
    bl_label = "OpenAI Voice Coach"
    bl_idname = "VIEW3D_PT_openai_voice"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OpenAICoach"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.openai_voice_coach", text="🎙️ Start")
        layout.operator("wm.openai_voice_coach_stop", text="🛑 Stop")

# === Registro ===
def register():
    bpy.utils.register_class(OpenAICoachOperator)
    bpy.utils.register_class(OpenAICoachStopOperator)
    bpy.utils.register_class(OpenAICoachPanel)

def unregister():
    bpy.utils.unregister_class(OpenAICoachOperator)
    bpy.utils.unregister_class(OpenAICoachStopOperator)
    bpy.utils.unregister_class(OpenAICoachPanel)

if __name__ == "__main__":
    register()
