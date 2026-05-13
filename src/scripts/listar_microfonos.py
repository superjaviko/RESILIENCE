import speech_recognition as sr

print("Micrófonos disponibles:")
for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {mic_name}")
