import speech_recognition as sr
import requests
import json
from gtts import gTTS
from pydub import AudioSegment
import os

# CONFIGURATION
CLAUDE_API_KEY = "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"  # ⬅️ Replace this
OUTPUT_AUDIO_PATH = "respuesta.mp3"

# Step 1 – Get voice input
def grabar_voz():
    r = sr.Recognizer()
    with sr.Microphone(device_index=2) as source:
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

# Step 2 – Send question to Claude AI
def preguntar_a_claude(texto):
    url = "https://api.anthropic.com/v1/messages"
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

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        mensaje = response.json()["content"][0]["text"]
        print("💬 Claude respondió:", mensaje)
        return mensaje
    else:
        print("⚠️ Error con Claude:", response.status_code, response.text)
        return "No se pudo obtener respuesta."

# Step 3 – Convertir texto a audio (gTTS)
def texto_a_audio(texto, ruta):
    tts = gTTS(text=texto, lang='it')
    tts.save(ruta)
    print(f"🔊 Audio guardado en: {ruta}")

# Main loop
def main():
    pregunta = grabar_voz()
    if not pregunta:
        return

    respuesta = preguntar_a_claude(pregunta)
    texto_a_audio(respuesta, OUTPUT_AUDIO_PATH)

    # (Opcional) Convert to WAV if needed by UPBGE
    sound = AudioSegment.from_mp3(OUTPUT_AUDIO_PATH)
    sound.export("respuesta.wav", format="wav")
    print("✅ Convertido a respuesta.wav para UPBGE")

if __name__ == "__main__":
    main()
