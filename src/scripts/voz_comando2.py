import speech_recognition as sr
import time
import os

ruta = os.path.join(os.path.dirname(__file__), "comando.txt")

recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=1)

def reconocer():
    with mic as source:
        print("🎤 Ascolto in corso...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        texto = recognizer.recognize_google(audio, language="it-IT")
        print("🗣️ Frase riconosciuta:", texto)
        return texto.lower()
    except sr.UnknownValueError:
        print("⚠️ Nessun riconoscimento.")
        return ""
    except sr.RequestError as e:
        print("❌ Errore Google:", e)
        return ""

# 🔁 Bucle infinito de escucha
print("🔁 Inizio ascolto continuo...")
while True:
    frase = reconocer()
    if frase:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(frase)
    time.sleep(1)  # Evita bucle excesivo
