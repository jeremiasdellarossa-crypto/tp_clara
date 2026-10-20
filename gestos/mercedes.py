
import threading
import time
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import pyttsx3
import ollama

dispositivo = 10
segundos = 8
reconocedor = sr.Recognizer()
detener_voz = threading.Event()
detener_voz.set()
hilo_voz = None
motor_voz = None

conversacion = [
    {
        "role": "system",
        "content": (
            "Tu nombre es Mercedes. "
            "Sos un holograma interactivo del proyecto HOLO-AI. "
            "Respondé en español argentino, de forma natural, "
            "clara y breve. Mantené el contexto de la conversación."
        )
    }
]


def hablar(texto):
    global motor_voz

    if detener_voz.is_set():
        return

    print("Mercedes:", texto)

    try:
        motor_voz = pyttsx3.init()
        motor_voz.setProperty("rate", 160)
        motor_voz.say(texto)
        motor_voz.runAndWait()

    except Exception as error:
        print("Error de voz:", error)

    finally:
        if motor_voz is not None:
            try:
                motor_voz.stop()
            except Exception:
                pass
        motor_voz = None


def escuchar_y_responder(evento):
    try:
        info = sd.query_devices(dispositivo, "input")
        frecuencia = int(info["default_samplerate"])
        print("Micrófono:", info["name"])

    except Exception as error:
        print("Error al encontrar el micrófono:", error)
        return

    while not evento.is_set():
        try:
            print("Escuchando...")

            audio = sd.rec(
                int(segundos * frecuencia),
                samplerate=frecuencia,
                channels=1,
                dtype="float32",
                device=dispositivo
            )
            sd.wait()

            if evento.is_set():
                break

            sf.write("voz.wav", audio, frecuencia)

            with sr.AudioFile("voz.wav") as fuente:
                audio_grabado = reconocedor.record(fuente)

            if evento.is_set():
                break

            texto = reconocedor.recognize_google(
                audio_grabado,
                language="es-AR"
            )

            print("Vos:", texto)

            comando = texto.lower().strip()

            if comando in [
                "salir",
                "apagate",
                "apagarte",
                "terminar",
                "terminá"
            ]:
                hablar("Está bien. Nos vemos.")
                evento.set()
                break

            conversacion.append({
                "role": "user",
                "content": texto
            })

            try:
                respuesta = ollama.chat(
                    model="llama3.2",
                    messages=conversacion
                )

                respuesta_ia = respuesta["message"]["content"]

            except Exception as error:
                conversacion.pop()
                print("Error de Ollama:", error)
                continue

            conversacion.append({
                "role": "assistant",
                "content": respuesta_ia
            })

            if not evento.is_set():
                hablar(respuesta_ia)

        except sr.UnknownValueError:
            if not evento.is_set():
                print("No entendí lo que dijiste.")

        except sr.RequestError as error:
            if not evento.is_set():
                print("Error del reconocimiento:", error)
                time.sleep(1)

        except Exception as error:
            if not evento.is_set():
                print("Error de escucha:", error)
            break

    print("Mercedes dejó de escuchar.")


def iniciar_voz():
    global detener_voz, hilo_voz

    if hilo_voz is not None and hilo_voz.is_alive():
        if not detener_voz.is_set():
            return

        print("Esperá a que termine de detenerse la voz.")
        return

    detener_voz = threading.Event()

    hilo_voz = threading.Thread(
        target=escuchar_y_responder,
        args=(detener_voz,),
        daemon=True
    )

    hilo_voz.start()


def apagar_voz():
    detener_voz.set()

    try:
        sd.stop()
    except Exception:
        pass

    if motor_voz is not None:
        try:
            motor_voz.stop()
        except Exception:
            pass
