import pygame
import cv2
import mediapipe as mp
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import ollama
import pyttsx3

import threading
import time
import os
import sys


# =========================================================
# CONFIGURACIÓN
# =========================================================

ANCHO = 800
ALTO = 600

DISPOSITIVO_MICROFONO = 10
FRECUENCIA_MICROFONO = 44100

SEGUNDOS_GRABACION = 5
ARCHIVO_AUDIO = "voz.wav"

MODELO_OLLAMA = "llama3.2"


# =========================================================
# INICIALIZAR PYGAME
# =========================================================

pygame.init()

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("HOLO-AI / HOLO-SIGN - Mercedes")

reloj = pygame.time.Clock()

fuente = pygame.font.SysFont("Arial", 22)
fuente_grande = pygame.font.SysFont("Arial", 30)


# =========================================================
# VARIABLES GENERALES
# =========================================================

ejecutando = True

procesando_voz = False
voz_hablando = False

ultimo_gesto = "IDLE"
gesto_actual = "IDLE"

mensaje = "Mercedes lista"


# =========================================================
# CLASE MERCEDES
# =========================================================

class Mercedes:

    def __init__(self):

        self.x = ANCHO // 2
        self.y = 350

        self.base_y = 350

        self.estado = "IDLE"

        self.wave_angle = 0
        self.wave_dir = 1

        self.crouch_offset = 0

        self.jump_offset = 0
        self.jump_speed = 0
        self.is_jumping = False

        self.estado_tiempo = 0

    # -----------------------------------------------------

    def cambiar_estado(self, estado, duracion=1.0):

        self.estado = estado
        self.estado_tiempo = time.time() + duracion

    # -----------------------------------------------------

    def izquierda(self):

        self.x -= 70

        if self.x < 120:
            self.x = 120

        self.cambiar_estado("MOVER_IZQ")

    # -----------------------------------------------------

    def derecha(self):

        self.x += 70

        if self.x > ANCHO - 120:
            self.x = ANCHO - 120

        self.cambiar_estado("MOVER_DER")

    # -----------------------------------------------------

    def arriba(self):

        self.y -= 60

        if self.y < 180:
            self.y = 180

        self.cambiar_estado("ARRIBA")

    # -----------------------------------------------------

    def abajo(self):

        self.y += 60

        if self.y > 430:
            self.y = 430

        self.cambiar_estado("ABAJO")

    # -----------------------------------------------------

    def saltar(self):

        if not self.is_jumping:

            self.is_jumping = True
            self.jump_speed = 15
            self.jump_offset = 0

            self.cambiar_estado("SALTAR", 1.5)

    # -----------------------------------------------------

    def agacharse(self):

        self.crouch_offset = 30

        self.cambiar_estado("AGACHARSE", 1.2)

    # -----------------------------------------------------

    def saludar(self):

        self.wave_angle = 0
        self.wave_dir = 1

        self.cambiar_estado("SALUDAR", 2.0)

    # -----------------------------------------------------

    def sorpresa(self):

        self.cambiar_estado("SORPRESA", 1.5)

    # -----------------------------------------------------

    def reposo(self):

        self.cambiar_estado("IDLE")

    # -----------------------------------------------------

    def actualizar(self):

        # -------------------------------
        # SALTO
        # -------------------------------

        if self.is_jumping:

            self.jump_offset -= self.jump_speed

            self.jump_speed -= 0.8

            if self.jump_offset >= 0:

                self.jump_offset = 0

                self.is_jumping = False

        # -------------------------------
        # AGACHARSE
        # -------------------------------

        if self.estado == "AGACHARSE":

            self.crouch_offset = 30

        else:

            if self.crouch_offset > 0:

                self.crouch_offset -= 2

        # -------------------------------
        # SALUDO
        # -------------------------------

        if self.estado == "SALUDAR":

            self.wave_angle += 6 * self.wave_dir

            if self.wave_angle > 30:

                self.wave_dir = -1

            if self.wave_angle < -30:

                self.wave_dir = 1

        else:

            self.wave_angle = 0

        # -------------------------------
        # ESTADO IDLE
        # -------------------------------

        if self.estado_tiempo != 0:

            if time.time() > self.estado_tiempo:

                self.estado = "IDLE"

        # -------------------------------
        # MOVIMIENTO SUAVE
        # -------------------------------

        if self.estado == "IDLE":

            self.y += (self.base_y - self.y) * 0.08

    # -----------------------------------------------------

    def dibujar(self, pantalla):

        self.actualizar()

        cx = int(self.x)

        cy = int(self.y + self.jump_offset)

        crouch = self.crouch_offset

        # =============================================
        # CABEZA
        # =============================================

        cabeza_y = cy - 120 + crouch

        pygame.draw.circle(
            pantalla,
            (0, 180, 255),
            (cx, cabeza_y),
            42
        )

        # Ojos

        pygame.draw.circle(
            pantalla,
            (0, 0, 0),
            (cx - 15, cabeza_y - 5),
            5
        )

        pygame.draw.circle(
            pantalla,
            (0, 0, 0),
            (cx + 15, cabeza_y - 5),
            5
        )

        # Boca

        pygame.draw.line(
            pantalla,
            (0, 0, 0),
            (cx - 12, cabeza_y + 15),
            (cx + 12, cabeza_y + 15),
            3
        )

        # =============================================
        # CUERPO
        # =============================================

        torso_y = cy - 65 + crouch

        pygame.draw.rect(
            pantalla,
            (0, 120, 220),
            (cx - 35, torso_y, 70, 100),
            border_radius=15
        )

        # =============================================
        # BRAZO IZQUIERDO
        # =============================================

        pygame.draw.line(
            pantalla,
            (0, 180, 255),
            (cx - 35, torso_y + 20),
            (cx - 90, torso_y + 70),
            12
        )

        # =============================================
        # BRAZO DERECHO
        # =============================================

        if self.estado == "SALUDAR":

            angulo = self.wave_angle

            brazo_x = cx + 35 + int(55 * pygame.math.Vector2(1, 0).rotate(-angulo).x)
            brazo_y = torso_y + 20 - int(55 * pygame.math.Vector2(1, 0).rotate(-angulo).y)

            pygame.draw.line(
                pantalla,
                (0, 180, 255),
                (cx + 35, torso_y + 20),
                (brazo_x, brazo_y),
                12
            )

            pygame.draw.circle(
                pantalla,
                (0, 180, 255),
                (brazo_x, brazo_y),
                15
            )

        else:

            pygame.draw.line(
                pantalla,
                (0, 180, 255),
                (cx + 35, torso_y + 20),
                (cx + 90, torso_y + 70),
                12
            )

        # =============================================
        # PIERNAS
        # =============================================

        pierna_inicio = torso_y + 100

        if self.estado == "AGACHARSE":

            largo_pierna = 45

        else:

            largo_pierna = 75

        pygame.draw.line(
            pantalla,
            (0, 150, 230),
            (cx - 18, pierna_inicio),
            (cx - 25, pierna_inicio + largo_pierna),
            14
        )

        pygame.draw.line(
            pantalla,
            (0, 150, 230),
            (cx + 18, pierna_inicio),
            (cx + 25, pierna_inicio + largo_pierna),
            14
        )

        # =============================================
        # TEXTO DE ESTADO
        # =============================================

        texto = fuente.render(
            "Mercedes: " + self.estado,
            True,
            (255, 255, 255)
        )

        pantalla.blit(
            texto,
            (20, 20)
        )


# =========================================================
# CREAR MERCEDES
# =========================================================

mercedes = Mercedes()


# =========================================================
# CÁMARA + MEDIAPIPE
# =========================================================

cap = cv2.VideoCapture(0)

camara_disponible = cap.isOpened()

if camara_disponible:

    mp_hands = mp.solutions.hands

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    )

else:

    print("No se pudo abrir la cámara.")
    hands = None


# =========================================================
# DETECTAR GESTO
# =========================================================

def detectar_gesto():

    global ultimo_gesto
    global gesto_actual

    if not camara_disponible:

        return "IDLE"

    ret, frame = cap.read()

    if not ret:

        return "IDLE"

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    resultados = hands.process(rgb)

    gesto = "IDLE"

    if resultados.multi_hand_landmarks:

        mano = resultados.multi_hand_landmarks[0]

        # Landmark 9 = centro de la mano

        hx = mano.landmark[9].x
        hy = mano.landmark[9].y

        # ---------------------------------------------
        # MANO ARRIBA
        # ---------------------------------------------

        if hy < 0.25:

            gesto = "SALTAR"

        # ---------------------------------------------
        # MANO A ALTURA MEDIA
        # ---------------------------------------------

        elif hy < 0.45:

            gesto = "SALUDAR"

        # ---------------------------------------------
        # MANO ABAJO
        # ---------------------------------------------

        elif hy > 0.75:

            gesto = "AGACHARSE"

        # ---------------------------------------------
        # MANO IZQUIERDA
        # ---------------------------------------------

        elif hx < 0.30:

            gesto = "MOVER_IZQ"

        # ---------------------------------------------
        # MANO DERECHA
        # ---------------------------------------------

        elif hx > 0.70:

            gesto = "MOVER_DER"

    gesto_actual = gesto

    return gesto


# =========================================================
# EJECUTAR GESTO
# =========================================================

def ejecutar_gesto(gesto):

    global mensaje

    if gesto == "SALTAR":

        mercedes.saltar()

        mensaje = "Gesto detectado: SALTAR"

    elif gesto == "SALUDAR":

        mercedes.saludar()

        mensaje = "Gesto detectado: SALUDAR"

    elif gesto == "AGACHARSE":

        mercedes.agacharse()

        mensaje = "Gesto detectado: AGACHARSE"

    elif gesto == "MOVER_IZQ":

        mercedes.izquierda()

        mensaje = "Gesto detectado: IZQUIERDA"

    elif gesto == "MOVER_DER":

        mercedes.derecha()

        mensaje = "Gesto detectado: DERECHA"


# =========================================================
# TEXTO A VOZ
# =========================================================

def hablar(texto):

    global voz_hablando

    voz_hablando = True

    try:

        voz = pyttsx3.init()

        voz.setProperty(
            "rate",
            160
        )

        voz.say(texto)

        voz.runAndWait()

        voz.stop()

    except Exception as error:

        print("Error de voz:", error)

    finally:

        voz_hablando = False


# =========================================================
# OLLAMA
# =========================================================

def preguntar_ollama(texto):

    try:

        respuesta = ollama.chat(
            model=MODELO_OLLAMA,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sos Mercedes, un robot holográfico "
                        "educativo. Respondé en español argentino, "
                        "de forma breve y natural."
                    )
                },
                {
                    "role": "user",
                    "content": texto
                }
            ]
        )

        return respuesta["message"]["content"]

    except Exception as error:

        print("Error Ollama:", error)

        return "No pude conectarme con mi inteligencia artificial."


# =========================================================
# PROCESAR VOZ
# =========================================================

def procesar_voz():

    global procesando_voz
    global mensaje

    if procesando_voz:

        return

    procesando_voz = True

    try:

        mensaje = "Escuchando..."

        print("\nGrabando...")

        audio = sd.rec(
            int(
                SEGUNDOS_GRABACION *
                FRECUENCIA_MICROFONO
            ),
            samplerate=FRECUENCIA_MICROFONO,
            channels=1,
            dtype="float32",
            device=DISPOSITIVO_MICROFONO
        )

        sd.wait()

        sf.write(
            ARCHIVO_AUDIO,
            audio,
            FRECUENCIA_MICROFONO
        )

        mensaje = "Procesando voz..."

        reconocedor = sr.Recognizer()

        with sr.AudioFile(ARCHIVO_AUDIO) as fuente:

            audio_sr = reconocedor.record(fuente)

        try:

            texto = reconocedor.recognize_google(
                audio_sr,
                language="es-AR"
            )

        except sr.UnknownValueError:

            mensaje = "No entendí lo que dijiste."

            print("No se entendió la voz.")

            return

        except sr.RequestError:

            mensaje = "No hay conexión para reconocer la voz."

            return

        print("\nVos dijiste:")
        print(texto)
        mensaje = "Vos: " + texto
        # =================================================
        # COMANDOS DE VOZ PARA MERCEDES
        # =================================================
        texto_minuscula = texto.lower()
        if "salta" in texto_minuscula:
            mercedes.saltar()
            respuesta = "¡Salto realizado!"
        elif "saludá" in texto_minuscula or "saluda" in texto_minuscula:
            mercedes.saludar()
            respuesta = "¡Hola!"
        elif "agachate" in texto_minuscula or "agáchate" in texto_minuscula:
            mercedes.agacharse()
            respuesta = "Me agacho."
        elif "izquierda" in texto_minuscula:
            mercedes.izquierda()
            respuesta = "Voy a la izquierda."
        elif "derecha" in texto_minuscula:
            mercedes.derecha()
            respuesta = "Voy a la derecha."
        elif "arriba" in texto_minuscula:
            mercedes.arriba()
            respuesta = "Voy para arriba."
        elif "abajo" in texto_minuscula:
            mercedes.abajo()
            respuesta = "Voy para abajo."
        else:
            # =============================================
            # SI NO ES UN COMANDO → OLLAMA
            # =============================================
            respuesta = preguntar_ollama(texto)
            mercedes.sorpresa()
        print("\nMercedes:")
        print(respuesta)
        mensaje = "Mercedes: " + respuesta[:55]
        hablar(respuesta)
    except Exception as error:
        print("\nError de voz:")
        print(error)
        mensaje = "Error con el micrófono."
    finally:
        procesando_voz = False
# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================
print("======================================")
print("       HOLO-AI / HOLO-SIGN")
print("======================================")
print()
print("Controles:")
print("ESPACIO = hablar")
print("J = saltar")
print("A = agacharse")
print("S = saludar")
print("FLECHAS = mover")
print("ESC = salir")
print()
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                ejecutando = False
            elif evento.key == pygame.K_SPACE:
                if not procesando_voz and not voz_hablando:
                    hilo = threading.Thread(
                        target=procesar_voz,
                        daemon=True
                    )
                    hilo.start()
            elif evento.key == pygame.K_LEFT:
                mercedes.izquierda()
            elif evento.key == pygame.K_RIGHT:
                mercedes.derecha()
            elif evento.key == pygame.K_UP:
                mercedes.arriba()
            elif evento.key == pygame.K_DOWN:
                mercedes.abajo()
            elif evento.key == pygame.K_j:
                mercedes.saltar()
            elif evento.key == pygame.K_a:
                mercedes.agacharse()
            elif evento.key == pygame.K_s:
                mercedes.saludar()
    if not procesando_voz and not voz_hablando:
        gesto = detectar_gesto()
        if gesto != ultimo_gesto:
            if gesto != "IDLE":
                ejecutar_gesto(gesto)
            ultimo_gesto = gesto
    pantalla.fill((0, 0, 0))
    mercedes.dibujar(pantalla)
    texto_gesto = fuente.render(
        "Gesto: " + gesto_actual,
        True,
        (255, 255, 255)
    )
    pantalla.blit(
        texto_gesto,
        (20, 55)
    )
    if camara_disponible:
        estado_camara = "Cámara: ACTIVA"
    else:
        estado_camara = "Cámara: NO DISPONIBLE"
    texto_camara = fuente.render(
        estado_camara,
        True,
        (255, 255, 255)
    )
    pantalla.blit(
        texto_camara,
        (20, 85)
    )
    texto_mensaje = fuente.render(
        mensaje[:70],
        True,
        (255, 255, 255)
    )
    pantalla.blit(
        texto_mensaje,
        (20, ALTO - 45)
    )
    pygame.display.flip()
    reloj.tick(60)
if cap is not None:
    cap.release()
if hands is not None:
    hands.close()
pygame.quit()
sys.exit()