
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import pyttsx3
import ollama
import time


# ==========================================
# CONFIGURACIÓN
# ==========================================

dispositivo = 10
segundos = 8

info = sd.query_devices(dispositivo, "input")
frecuencia = int(info["default_samplerate"])


# ==========================================
# RECONOCIMIENTO DE VOZ
# ==========================================

reconocedor = sr.Recognizer()


# ==========================================
# MEMORIA DE LA CONVERSACIÓN
# ==========================================

conversacion = [
    {
        "role": "system",
        "content": (
            "Tu nombre es Mercedes. "
            "Sos un holograma interactivo del proyecto HOLO-AI. "
            "Respondé en español argentino de forma natural, clara y breve. "
            "Mantené el contexto de la conversación. "
            "No hagas respuestas demasiado largas porque después tenés que decirlas en voz alta."
        )
    }
]


# ==========================================
# FUNCIÓN PARA QUE MERCEDES HABLE
# ==========================================

def hablar(texto):

    print()
    print("Mercedes:")
    print(texto)
    print()

    try:

        # Crear un motor nuevo cada vez
        voz = pyttsx3.init()

        voz.setProperty("rate", 160)

        voz.say(texto)

        voz.runAndWait()

        # Cerrar el motor
        voz.stop()

        # Pequeña pausa antes de volver a escuchar
        time.sleep(1)

    except Exception as error:

        print("Error de voz:")
        print(error)


# ==========================================
# FUNCIÓN PARA GRABAR
# ==========================================

def grabar():

    print("--------------------------------------")
    print("Escuchando...")
    print("Tenés", segundos, "segundos para hablar.")

    try:

        # Detener cualquier grabación anterior
        sd.stop()

        time.sleep(0.3)

        audio = sd.rec(
            int(segundos * frecuencia),
            samplerate=frecuencia,
            channels=1,
            dtype="float32",
            device=dispositivo
        )

        sd.wait()

        sf.write(
            "voz.wav",
            audio,
            frecuencia
        )

        print("Grabación terminada.")

        return True

    except Exception as error:

        print("Error del micrófono:")
        print(error)

        return False


# ==========================================
# PRESENTACIÓN
# ==========================================

print("======================================")
print("          MERCEDES - HOLO-AI")
print("======================================")
print()

print("Micrófono:", info["name"])
print("Frecuencia:", frecuencia)
print()

hablar(
    "Hola, soy Mercedes. "
    "Estoy lista para hablar."
)


# ==========================================
# CONVERSACIÓN CONTINUA
# ==========================================

while True:

    # --------------------------------------
    # GRABAR
    # --------------------------------------

    grabacion_correcta = grabar()


    if not grabacion_correcta:

        print()
        print("No pude acceder al micrófono.")
        print("Voy a intentar nuevamente.")
        print()

        time.sleep(2)

        continue


    # --------------------------------------
    # RECONOCIMIENTO DE VOZ
    # --------------------------------------

    print("Reconociendo voz...")


    try:

        with sr.AudioFile("voz.wav") as fuente:

            audio_grabado = reconocedor.record(fuente)


        texto = reconocedor.recognize_google(
            audio_grabado,
            language="es-AR"
        )


    except sr.UnknownValueError:

        print()
        print("No pude entender lo que dijiste.")
        print("Volviendo a escuchar...")
        print()

        continue


    except sr.RequestError:

        print()
        print("No se pudo conectar con el reconocimiento de voz.")
        print()

        continue


    # --------------------------------------
    # MOSTRAR LO QUE DIJISTE
    # --------------------------------------

    print()
    print("Vos:")
    print(texto)
    print()


    # --------------------------------------
    # COMANDO PARA SALIR
    # --------------------------------------

    comando = texto.lower().strip()


    if comando in [
        "salir",
        "apagate",
        "apagarte",
        "terminar",
        "terminá"
    ]:

        hablar(
            "Está bien. "
            "Nos vemos."
        )

        break


    # --------------------------------------
    # GUARDAR MENSAJE EN LA MEMORIA
    # --------------------------------------

    conversacion.append(
        {
            "role": "user",
            "content": texto
        }
    )


    # --------------------------------------
    # OLLAMA
    # --------------------------------------

    print("Mercedes está pensando...")
    print()


    try:

        respuesta = ollama.chat(
            model="llama3.2",
            messages=conversacion
        )


        respuesta_ia = respuesta["message"]["content"]


    except Exception as error:

        print("Error con Ollama:")
        print(error)
        print()

        # Sacar el último mensaje del usuario
        # para no dejar la conversación incompleta
        conversacion.pop()

        continue


    # --------------------------------------
    # GUARDAR RESPUESTA EN LA MEMORIA
    # --------------------------------------

    conversacion.append(
        {
            "role": "assistant",
            "content": respuesta_ia
        }
    )


    # --------------------------------------
    # MERCEDES HABLA
    # --------------------------------------

    hablar(respuesta_ia)


    # --------------------------------------
    # VOLVER A ESCUCHAR
    # --------------------------------------

    print("Mercedes terminó de hablar.")
    print("Preparándose para escucharte nuevamente...")
    print()

    time.sleep(1)


# ==========================================
# FINAL
# ==========================================

print()
print("======================================")
print("Mercedes se apagó.")
print("======================================")
