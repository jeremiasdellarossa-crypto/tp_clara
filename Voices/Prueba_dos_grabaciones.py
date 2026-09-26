
import sounddevice as sd
import soundfile as sf
import pyttsx3
import time

dispositivo = 10
frecuencia = 44100

voz = pyttsx3.init()
voz.setProperty("rate", 160)


print("================================")
print("      PRUEBA MICROFONO")
print("================================")
print()

print("Primero Mercedes va a hablar.")

voz.say("Hola. Cuando termine de hablar, esperá.")
voz.runAndWait()

# IMPORTANTE:
# Esperar antes de volver a usar el micrófono
time.sleep(3)

print()
print("================================")
print("AHORA SI")
print("================================")
print()
print("HABLÁ DURANTE 5 SEGUNDOS.")
print("EMPIEZA EN 3...")
time.sleep(1)

print("2...")
time.sleep(1)

print("1...")
time.sleep(1)

print("HABLÁ AHORA.")

try:

    audio = sd.rec(
        int(5 * frecuencia),
        samplerate=frecuencia,
        channels=1,
        dtype="float32",
        device=dispositivo
    )

    sd.wait()

    sf.write(
        "prueba_despues_de_voz.wav",
        audio,
        frecuencia
    )

    print()
    print("GRABACIÓN TERMINADA")
    print("Muestras grabadas:", len(audio))

except Exception as error:

    print()
    print("ERROR:")
    print(error)


print()
print("Prueba terminada.")
