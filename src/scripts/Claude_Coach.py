# Claude Coach Addon para UPBGE (actualizado con hilos y HUD VR)
# Versión enfocada a "Coach Contextual" (Opcion E) en italiano

bl_info = {
    "name": "Claude Voice Coach",
    "blender": (3, 6, 0),
    "category": "Game Engine",
    "author": "Javier E. Suarez Savigne",
    "description": "Claude Voice Assistant + Operation Workflow Kwnoledge"
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

# VARIABLES GLOBALES
CLAUDE_API_KEY ="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"
PROCEDIMIENTO_PATH = os.path.join(os.path.dirname(__file__), "procedura.json")
AUDIO_TEMP_PATH = os.path.join(tempfile.gettempdir(), "risposta_coach.mp3")
esecuzione_attiva = True  # Variable global para controlar el bucle

# FUNCIONES

def carica_procedura():
    try:
        with open(PROCEDIMIENTO_PATH, "r", encoding="utf-8") as f:
            procedura = json.load(f)
        return procedura
    except Exception as e:
        print("❌ Errore nel caricamento della procedura:", e)
        return None

def costruisci_contesto(domanda, procedura):
    passi = "\n".join([
        f"Passaggio {p['paso']}: {p['titolo']} - {p['dettaglio']}"
        for p in procedura.get("procedura", [])
    ])
    contesto = (
        f"Sei un assistente esperto che guida l'operatore in tempo reale."
        f"L'operatore deve seguire una procedura per il controllo del allarme Mancanza di flusso acqua raffreddamento."
        f"L'operatore deve capire cosa sta sucedendo nel pulpito, specificamente deve controllare lo stato del allarme."
        f"Puoi rispondere solo in base alla seguente procedura:\n{passi}\n"
        f"Domanda dell'operatore: {domanda}\n"
        f"Ricorda: non inventare passaggi. Se non è definito, di' che non è nella procedura."
    )
    return contesto

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

def chiedi_a_claude(testo):
    if not CLAUDE_API_KEY:
        print("⚠️ CLAUDE_API_KEY non è configurata come variabile di ambiente")
        return "Chiave API non configurata."

    procedura = carica_procedura()
    if not procedura:
        return "Impossibile caricare la procedura."

    contesto = costruisci_contesto(testo, procedura)

    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 200,
        "messages": [
            {"role": "user", "content": contesto}
        ]
    }

    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        messaggio = response.json()["content"][0]["text"]
        print("💬 Claude ha risposto:", messaggio)
        return messaggio
    else:
        print("⚠️ Errore con Claude:", response.status_code, response.text)
        return "Non è stato possibile ottenere una risposta."

def riproduci_audio(testo):
    tts = gTTS(text=testo, lang='it')
    tts.save(AUDIO_TEMP_PATH)
    sound = AudioSegment.from_mp3(AUDIO_TEMP_PATH)
    wav_path = AUDIO_TEMP_PATH.replace(".mp3", ".wav")
    sound.export(wav_path, format="wav")
    subprocess.call(["powershell", "-c", f"(New-Object Media.SoundPlayer '{wav_path}').PlaySync()"])


def flusso_coach():
    global esecuzione_attiva
    while esecuzione_attiva:
        domanda = registra_voce()
        if not domanda:
            print("❌ Nessuna voce riconosciuta. Riprovo...")
            continue
        risposta = chiedi_a_claude(domanda)
        riproduci_audio(risposta)
        time.sleep(1)  # Breve pausa per evitare doppie acquisizioni

class ClaudeCoachOperator(bpy.types.Operator):
    bl_idname = "wm.claude_voice_coach"
    bl_label = "Talk to Claude"

    def execute(self, context):
        threading.Thread(target=flusso_coach).start()
        return {'FINISHED'}

class ClaudeCoachPanel(bpy.types.Panel):
    bl_label = "Claude Voice Coach"
    bl_idname = "VIEW3D_PT_claude_coach"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ClaudeCoach"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.claude_voice_coach", text="🎙️ Start Claude")
        layout.operator("wm.claude_voice_coach_stop", text="🛑 Stop Claude")

class ClaudeCoachStopOperator(bpy.types.Operator):
    bl_idname = "wm.claude_voice_coach_stop"
    bl_label = "Stop Claude"

    def execute(self, context):
        global esecuzione_attiva
        esecuzione_attiva = False
        self.report({'INFO'}, "Claude disattivato.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ClaudeCoachOperator)
    bpy.utils.register_class(ClaudeCoachStopOperator)
    bpy.utils.register_class(ClaudeCoachPanel)

def unregister():
    bpy.utils.unregister_class(ClaudeCoachOperator)
    bpy.utils.unregister_class(ClaudeCoachStopOperator)
    bpy.utils.unregister_class(ClaudeCoachPanel)

if __name__ == "__main__":
    register()