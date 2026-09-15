import sounddevice as sd
import soundfile as sf
dispositivo = 10
segundos = 8
info = sd.query_devices(dispositivo, "input")
print("Micrófono:")
print(info["name"])
print("Frecuencia:", info["default_samplerate"])
frecuencia = int(info["default_samplerate"])
print()
print("Hablá durante 8 segundos...")
audio = sd.rec(
    int(segundos * frecuencia),
    samplerate=frecuencia,
    channels=1,
    device=dispositivo
)
sd.wait()
sf.write("voz.wav", audio, frecuencia)
print("Grabación terminada.")
print("Audio guardado como voz.wav")