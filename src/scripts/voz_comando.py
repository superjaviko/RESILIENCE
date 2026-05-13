import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone(device_index=1) as source:  # Usa tu índice correcto
    print("🎙️ Calibrando ruido ambiente...")
    r.adjust_for_ambient_noise(source, duration=1)
    print("🎙️ Di un comando...")

    audio = r.listen(source)

try:
    texto = r.recognize_google(audio, language="it-IT").lower()
    print("✅ Dijiste:", texto)

    with open("comando.txt", "w", encoding="utf-8") as f:
        f.write(texto)

except sr.UnknownValueError:
    print("❌ No entendí lo que dijiste.")
except sr.RequestError as e:
    print("⚠️ Error al conectar:", e)

