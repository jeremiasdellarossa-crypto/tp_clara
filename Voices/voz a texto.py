import sounddevice as sd
import soundfile as sf
import speech_recognition as sr

# Configuración
dispositivo = 10
segundos = 8

# Obtener información del micrófono
info = sd.query_devices(dispositivo, "input")
frecuencia = 48000

print("Micrófono:", info["name"])
print("Hablá durante 8 segundos...")

# Grabar
audio = sd.rec(
    int(segundos * frecuencia),
    samplerate=frecuencia,
    channels=1,
    device=dispositivo
)

sd.wait()

# Guardar grabación
sf.write("voz.wav", audio, frecuencia)

print("Grabación terminada.")
print("Reconociendo voz...")

# Convertir voz a texto
reconocedor = sr.Recognizer()

with sr.AudioFile("voz.wav") as fuente:
    audio_grabado = reconocedor.record(fuente)

try:
    texto = reconocedor.recognize_google(
        audio_grabado,
        language="es-AR"
    )

    print()
    print("Vos dijiste:")
    print(texto)

except sr.UnknownValueError:
    print("No pude entender lo que dijiste.")

except sr.RequestError:
    print("No se pudo conectar con el reconocimiento de voz.")