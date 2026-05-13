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
manager = bge.logic.getCurrentScene().objects["GameManager"]

if manager["game_state"] == "audio_active":
    interrompi_audio()
    print("⛔ LM Coach bloqueado porque un audio del sistema 1 está en reproducción.")
    
    
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
        f"L'operatore deve disattivare l'allarme entro il tempo indicato sul Quadro MD02.\n"
        f"L'operatore deve capire cosa sta succedendo nel pulpito, specificamente deve controllare lo stato dell'allarme.\n"
        f"Puoi rispondere solo in base alla seguente procedura:\n{passi}\n"
        f"Domanda dell'operatore: {domanda}\n"
        f"Ricorda: non inventare passaggi. Se non è definito, di' che non è nella procedura.\n"
        f"Quando l'esecuzione di un'operazione richiede troppo tempo, bisogna affrettarsi."
        f"Esempio:\n"
        f"Domanda: Come verifico lo stato dell'allarme?\n"
        f"Risposta: Controlla la spia rossa sul pannello principale.\n"
        f"Domanda: " + domanda + "\n"
        )

def registra_voce():
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        print("🎙️ Parla ora...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        testo_raw = r.recognize_google(audio, language="it-IT")
        print(f"✅ Riconosciuto (grezzo): {testo_raw}")
        testo = preelabora_input(testo_raw)
        print(f"🔎 Dopo pre-elaborazione: {testo}")
        return testo
    except Exception as e:
        print("❌ Errore nel riconoscimento vocale:", e)
        return None
    
def pulisci_testo(testo):
    frasi_inutili = [
        "per favore", "puoi dirmi", "vorrei sapere", "mi potresti dire",
        "ciao", "salve", "gentilmente", "potresti"
    ]
    
    for frase in frasi_inutili:
        testo = testo.replace(frase, "")
    return testo.strip()

    
def correggi_intenzione(testo):
    dizionario_sinonimi = {
        "spia": "indicatore",
        "luce rossa": "indicatore",
        "allarme acqua": "allarme",
        "verifica": "controlla",
        "controllare": "controlla",
        "guardare": "controlla",
        "accensione": "attivazione",
        "spegnere": "disattivare"
    }

    for chiave, valore in dizionario_sinonimi.items():
        testo = testo.replace(chiave, valore)
    return testo

def preelabora_input(testo):
    testo = testo.strip().lower()
    testo = pulisci_testo(testo)
    testo = correggi_intenzione(testo)
    return testo

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
        print("🔇 LM Coach detenido.")
    
    # ✅ Muy importante: cambiar estado si accede a GameManager
    try:
        from bge import logic
        manager = logic.getCurrentScene().objects["GameManager"]
        manager["game_state"] = "idle"
    except:
        print("⚠️ No se pudo actualizar game_state a idle.")
        
def interrompi_coach_se_audio():
    manager = bge.logic.getCurrentScene().objects["GameManager"]
    if manager["game_state"] == "coach_active":
        interrompi_audio()
        manager["game_state"] = "idle"
        print("🔇 LM Coach interrotto da audio guidato.")

def flusso_coach():
    domanda_raw = registra_voce()
    if not domanda_raw:
        print("❌ Nessuna voce riconosciuta.")
        return

    domanda = preelabora_input(domanda_raw)
    print("🧠 Domanda pre-elaborata:", domanda)

    risposta = chiedi_a_llm(domanda)
    riproduci_audio(risposta)
    time.sleep(2)  # Pausa antes de permitir otra colisión
    
def reset_coach(own):
    time.sleep(5)  # esperar suficiente para que termine la interacción
    own["coach_attivo"] = False
    print("🎤 Coach desactivado, listo para próxima colisión.")
    
def main(cont):
    own = cont.owner
    if own.sensors["Collision"].positive and not own.get("coach_attivo", False):
        own["coach_attivo"] = True
        print("🎤 LM Stdio attivato da collisione")
        # Reproduce saludo inicial
        manager["game_state"]="coach_active"
        riproduci_audio("Ciao, come ti posso aiutare?")
        # Ejecuta una vez el ciclo de escucha-respuesta
        threading.Thread(target=flusso_coach).start()
        
        # Al terminar flusso_coach, desactivamos coach_attivo para permitir nuevas colisiones
        threading.Thread(target=reset_coach, args=(own,)).start()

        
    if own.sensors["Collision.001"].positive and not own.get("coach_attivo", False):
        own["coach_attivo"] = True
        print("🎤 LM Stdio attivato da collisione")
        # Reproduce saludo inicial
        manager["game_state"]="coach_active"
        print("🎤 LM Stdio attivato da collisione")
        riproduci_audio("Ciao, come ti posso aiutare?")
        # Ejecuta una vez el ciclo de escucha-respuesta
        threading.Thread(target=flusso_coach).start()
        
        # Al terminar flusso_coach, desactivamos coach_attivo para permitir nuevas colisiones
        threading.Thread(target=reset_coach, args=(own,)).start()

