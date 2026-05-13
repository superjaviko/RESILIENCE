import speech_recognition as sr
import requests
import json
from gtts import gTTS
from pydub import AudioSegment
import os
import time

# CONFIGURACIÓN
CLAUDE_API_KEY = "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"  # 🔐 Reemplaza con tu clave real
API_URL = "https://api.anthropic.com/v1/messages"
HEADERS = {
    "x-api-key": CLAUDE_API_KEY,
    "anthropic-version": "2023-06-01",
    "Content-Type": "application/json"
}
OUTPUT_MP3 = "respuesta.mp3"
OUTPUT_WAV = "respuesta.wav"

# 🎙️ Captura de voz
def escuchar_microfono():
    r = sr.Recognizer()
    with sr.Microphone(device_index=2) as source:
        print("\n🎧 Parla ora (modo continuo)...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        texto = r.recognize_google(audio, language="it-IT")
        print(f"🗣️ Hai detto: {texto}")
        return texto
    except sr.UnknownValueError:
        print("❌ Non capito, riprova.")
        return None
    except sr.RequestError as e:
        print("⚠️ Errore di connessione:", e)
        return None

# 📡 Enviar a Claude AI
def preguntar_a_claude(texto):
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 500,
        "messages": [
            {"role": "user", "content": texto}
        ]
    }
    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
    if response.status_code == 200:
        mensaje = response.json()["content"][0]["text"]
        print("🤖 Claude risponde:", mensaje)
        return mensaje
    else:
        print("⚠️ Errore Claude:", response.status_code, response.text)
        return "Non ho potuto rispondere alla tua richiesta."

# 🔊 Generar audio
def convertir_a_audio(texto):
    try:
        tts = gTTS(text=texto, lang='it')
        tts.save(OUTPUT_MP3)
        print("🔊 Audio salvato in MP3")

        sound = AudioSegment.from_mp3(OUTPUT_MP3)
        sound.export(OUTPUT_WAV, format="wav")
        print("✅ risposta.wav generato")
    except Exception as e:
        print("⚠️ Errore durante la generazione audio:", e)

# 🔁 Loop continuo
def main():
    print("🎤 Assistant vocale Claude attivo (modalità continua)\n")
    while True:
        frase = escuchar_microfono()
        if frase:
            risposta = preguntar_a_claude(frase)
            convertir_a_audio(risposta)

        # Espera a que UPBGE reproduzca el audio y elimine el archivo
        while os.path.exists(OUTPUT_WAV):
            print("🕒 Aspettando che UPBGE riproduca risposta.wav...")
            time.sleep(1)

if __name__ == "__main__":
    main()

