import sounddevice as sd

dispositivo = 9

print("Información del micrófono:")
print(sd.query_devices(dispositivo))

print("\nFrecuencia predeterminada:")

info = sd.query_devices(dispositivo, "input")
print(info["default_samplerate"])