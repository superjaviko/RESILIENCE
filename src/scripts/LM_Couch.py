import bge
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

# === VARIABLES GLOBALES ===
PROCEDURA_PATH = bge.logic.expandPath("//procedura.json")
AUDIO_TEMP_PATH = os.path.join(tempfile.gettempdir(), "risposta_coach.mp3")
esecuzione_attiva = True
player = None  # Para controlar el audio

# === FUNCIONES ===

def carica_procedura():
    try:
        with open(PROCEDURA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("❌ Errore nel caricamento della procedura:", e)
        return None

def costruisci_contesto(domanda, procedura):
    passi = "\n".join([
        f"Passaggio {p['paso']}: {p['titolo']} - {p['dettaglio']}"
        for p in procedura.get("procedura", [])
    ])
    return (
        f"Sei un assistente esperto che guida l'operatore in tempo reale. Devi parlare sempre en seconda persona in modo imperativo\n"
        f"L'operatore deve seguire una procedura per il controllo dell'allarme 'Mancanza di flusso acqua raffreddamento'.\n"
        f"L'operatore deve capire cosa sta succedendo nel pulpito, specificamente deve controllare lo stato dell'allarme.\n"
        f"Puoi rispondere solo in base alla seguente procedura:\n{passi}\n"
        f"Domanda dell'operatore: {domanda}\n"
        f"Ricorda: non inventare passaggi. Se non è definito, di' che non è nella procedura."
    )

def registra_voce():
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
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

def chiedi_a_llm(testo):
    procedura = carica_procedura()
    if not procedura:
        return "Procedura non disponibile."

    contesto = costruisci_contesto(testo, procedura)
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "local-model",  # No necesario especificar en LM Studio normalmente
        "messages": [
            {"role": "user", "content": contesto}
        ],
        "max_tokens": 200
    }

    try:
        response = requests.post("http://localhost:1234/v1/chat/completions", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            message = response.json()["choices"][0]["message"]["content"]
            print("💬 LLM ha risposto:", message)
            return message
        else:
            print("⚠️ Errore LM Studio:", response.status_code, response.text)
            return "Errore di comunicazione con LLM."
    except Exception as e:
        print("❌ Connessione fallita:", e)
        return "Errore di rete."

def riproduci_audio(testo):
    global player
    tts = gTTS(text=testo, lang='it')
    tts.save(AUDIO_TEMP_PATH)
    sound = AudioSegment.from_mp3(AUDIO_TEMP_PATH)
    wav_path = AUDIO_TEMP_PATH.replace(".mp3", ".wav")
    sound.export(wav_path, format="wav")

    # Usa subprocess non bloqueante
    player = subprocess.Popen([
        "powershell",
        "-c",
        f"$p = New-Object Media.SoundPlayer '{wav_path}'; $p.Play(); Start-Sleep 9999"
    ])

def interrompi_audio():
    global player
    if player and player.poll() is None:
        player.terminate()
        print("🔇 Audio interrotto.")

def flusso_coach():
    global esecuzione_attiva
    while esecuzione_attiva:
        domanda = registra_voce()
        if not domanda:
            print("❌ Nessuna voce riconosciuta.")
            continue
        risposta = chiedi_a_llm(domanda)
        riproduci_audio(risposta)
        time.sleep(1)

def main(cont):
    own = cont.owner
    if own.sensors["Collision"].positive and not own.get("coach_attivo", False):
        own["coach_attivo"] = True
        print("🎤 LM Stdio attivato da collisione")
        # Reproduce saludo inicial
        riproduci_audio("Ciao, come ti posso aiutare?")
        threading.Thread(target=flusso_coach).start()