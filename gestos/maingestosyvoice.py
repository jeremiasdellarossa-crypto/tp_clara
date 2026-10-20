
import cv2
import pygame
import mediapipe as mp
import sys
import time
import math
import mercedes
from gesto import Mercedes

pygame.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("HOLO-AI / HOLO-SIGN - Control por Camara")

reloj = pygame.time.Clock()
NEGRO = (0, 0, 0)
AZUL = (0, 153, 255)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)

fuente = pygame.font.SysFont("Arial", 22)
fuente_chica = pygame.font.SysFont("Arial", 16)

robot = Mercedes()

cuerpo_base = None
postura_anterior = "NORMAL"
contador_salto = 0
mano_anterior = "NINGUNO"
tiempo_salto = 0
voz_activa = False

camara = None

for indice in range(3):
    prueba = cv2.VideoCapture(indice, cv2.CAP_DSHOW)
    if prueba.isOpened():
        correcto, imagen = prueba.read()
        if correcto:
            camara = prueba
            print("Camara abierta:", indice)
            break
    prueba.release()

if camara is None:
    for indice in range(3):
        prueba = cv2.VideoCapture(indice)
        if prueba.isOpened():
            correcto, imagen = prueba.read()
            if correcto:
                camara = prueba
                print("Camara abierta:", indice)
                break
        prueba.release()

try:
    mp_pose = mp.solutions.pose
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
except AttributeError:
    import mediapipe.python.solutions.pose as mp_pose
    import mediapipe.python.solutions.hands as mp_hands
    import mediapipe.python.solutions.drawing_utils as mp_drawing

postura = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

manos = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def dibujar_robot():
    x = max(70, min(ANCHO - 70, int(robot.x)))
    y = max(130, min(ALTO - 120, int(robot.y)))

    agachado = robot.estado == "agacharse"

    if agachado:
        cabeza_y = y - 40
        cuerpo_y = y
        cuerpo_alto = 60
        pecho_y = y + 25
        brazo_inicio_y = y + 10
        brazo_final_y = y + 30
        pierna_inicio_y = y + 60
        pierna_final_y = y + 80
    else:
        cabeza_y = y - 75
        cuerpo_y = y - 25
        cuerpo_alto = 90
        pecho_y = y + 20
        brazo_inicio_y = y - 15
        brazo_final_y = y + 40
        pierna_inicio_y = y + 65
        pierna_final_y = y + 115

    pygame.draw.circle(pantalla, AZUL, (x, cabeza_y), 40)
    pygame.draw.circle(pantalla, NEGRO, (x - 14, cabeza_y - 5), 6)
    pygame.draw.circle(pantalla, NEGRO, (x + 14, cabeza_y - 5), 6)

    pygame.draw.rect(
        pantalla, AZUL,
        (x - 35, cuerpo_y, 70, cuerpo_alto),
        border_radius=12
    )

    pygame.draw.circle(pantalla, BLANCO, (x, pecho_y), 10)

    pygame.draw.line(
        pantalla, AZUL,
        (x - 34, brazo_inicio_y),
        (x - 64, brazo_final_y),
        13
    )

    if robot.estado == "saludar":
        pygame.draw.line(
            pantalla, AZUL,
            (x + 34, brazo_inicio_y),
            (x + 55, brazo_inicio_y - 45),
            13
        )
    else:
        pygame.draw.line(
            pantalla, AZUL,
            (x + 34, brazo_inicio_y),
            (x + 64, brazo_final_y),
            13
        )

    if agachado:
        pygame.draw.line(
            pantalla, AZUL,
            (x - 20, pierna_inicio_y),
            (x - 32, pierna_final_y),
            18
        )
        pygame.draw.line(
            pantalla, AZUL,
            (x + 20, pierna_inicio_y),
            (x + 32, pierna_final_y),
            18
        )
    else:
        pygame.draw.rect(
            pantalla, AZUL,
            (x - 25, pierna_inicio_y, 18, 50),
            border_radius=5
        )
        pygame.draw.rect(
            pantalla, AZUL,
            (x + 7, pierna_inicio_y, 18, 50),
            border_radius=5
        )


def mejorar_imagen(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )
    l = clahe.apply(l)
    imagen = cv2.merge((l, a, b))
    imagen = cv2.cvtColor(imagen, cv2.COLOR_LAB2BGR)
    return cv2.convertScaleAbs(imagen, alpha=1.2, beta=15)


def detectar_gesto(frame):
    global cuerpo_base, postura_anterior
    global contador_salto, mano_anterior, tiempo_salto

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado_pose = postura.process(rgb)
    resultado_manos = manos.process(rgb)
    accion = "NORMAL"

    if resultado_pose.pose_landmarks:
        puntos = resultado_pose.pose_landmarks.landmark
        hombro_izq = puntos[11]
        hombro_der = puntos[12]

        if (
            hombro_izq.visibility > 0.6
            and hombro_der.visibility > 0.6
        ):
            hombros_y = (hombro_izq.y + hombro_der.y) / 2

            if cuerpo_base is None:
                cuerpo_base = hombros_y

            diferencia = hombros_y - cuerpo_base

            if diferencia > 0.05:
                accion = "AGACHARSE"
                contador_salto = 0

            elif diferencia < -0.018:
                contador_salto += 1
                if contador_salto >= 2:
                    accion = "SALTAR"

            else:
                contador_salto = 0
                cuerpo_base = (
                    0.995 * cuerpo_base + 0.005 * hombros_y
                )

            if accion != postura_anterior:
                if accion == "AGACHARSE":
                    robot.agacharse()

                elif accion == "SALTAR":
                    robot.saltar()
                    tiempo_salto = time.time()

                elif accion == "NORMAL":
                    if postura_anterior == "AGACHARSE":
                        robot.reposo()

                postura_anterior = accion

            mp_drawing.draw_landmarks(
                frame,
                resultado_pose.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

            cv2.putText(
                frame,
                f"Movimiento: {diferencia:.3f}",
                (10, 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2
            )
    else:
        accion = "SIN PERSONA"

    mano_actual = "NINGUNO"

    if resultado_manos.multi_hand_landmarks:
        for mano in resultado_manos.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, mano, mp_hands.HAND_CONNECTIONS
            )

        if accion not in ("AGACHARSE", "SALTAR"):
            mano = resultado_manos.multi_hand_landmarks[0]
            hx = mano.landmark[0].x
            hy = mano.landmark[0].y

            if hy < 0.60:
                mano_actual = "SALUDAR"
            elif hx < 0.35:
                mano_actual = "MOVER IZQUIERDA"
            elif hx > 0.65:
                mano_actual = "MOVER DERECHA"

            if mano_actual != mano_anterior:
                if mano_actual == "SALUDAR":
                    robot.saludar()
                elif mano_actual == "MOVER IZQUIERDA":
                    robot.izquierda()
                elif mano_actual == "MOVER DERECHA":
                    robot.derecha()

    mano_anterior = mano_actual

    cv2.putText(
        frame,
        "POSTURA: " + accion,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        VERDE,
        2
    )

    cv2.putText(
        frame,
        "MANO: " + mano_actual,
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        VERDE,
        2
    )

    return accion, frame


def cambiar_voz():
    global voz_activa

    if not voz_activa:
        mercedes.iniciar_voz()
        voz_activa = True
        print("Mercedes esta escuchando.")
    else:
        mercedes.apagar_voz()
        voz_activa = False
        print("Mercedes dejo de escuchar.")


ejecutando = True
ultimo_gesto = "SIN PERSONA"

try:
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False
                elif evento.key == pygame.K_SPACE:
                    cambiar_voz()
                elif evento.key == pygame.K_LEFT:
                    robot.izquierda()
                elif evento.key == pygame.K_RIGHT:
                    robot.derecha()
                elif evento.key == pygame.K_UP:
                    robot.arriba()
                elif evento.key == pygame.K_DOWN:
                    robot.abajo()

        correcto, frame = camara.read() if camara is not None else (False, None)
        imagen_pygame = None

        if correcto:
            frame = cv2.flip(frame, 1)
            frame = mejorar_imagen(frame)
            ultimo_gesto, frame = detectar_gesto(frame)

            miniatura = cv2.resize(frame, (180, 135))
            rgb = cv2.cvtColor(miniatura, cv2.COLOR_BGR2RGB)
            imagen_pygame = pygame.surfarray.make_surface(
                rgb.swapaxes(0, 1)
            )

        if tiempo_salto and time.time() - tiempo_salto >= 0.35:
            robot.y += 50
            if robot.estado == "saltar":
                robot.reposo()
            tiempo_salto = 0

        robot.x = max(70, min(ANCHO - 70, robot.x))
        robot.y = max(130, min(ALTO - 120, robot.y))

        pantalla.fill(NEGRO)
        dibujar_robot()

        if imagen_pygame is not None:
            x_camara = ANCHO - 190
            y_camara = 20
            pantalla.blit(imagen_pygame, (x_camara, y_camara))
            pygame.draw.rect(
                pantalla, BLANCO,
                (x_camara, y_camara, 180, 135), 2
            )
        else:
            texto = fuente_chica.render(
                "Camara no disponible", True, BLANCO
            )
            pantalla.blit(texto, (ANCHO - 190, 40))

        texto_estado = fuente.render(
            "DETECCION: " + ultimo_gesto,
            True,
            BLANCO
        )
        pantalla.blit(
            texto_estado,
            (
                ANCHO // 2 - texto_estado.get_width() // 2,
                ALTO - 35
            )
        )

        pygame.display.flip()
        reloj.tick(30)

finally:
    try:
        mercedes.apagar_voz()
    except Exception:
        pass

    if camara is not None:
        camara.release()

    manos.close()
    postura.close()
    cv2.destroyAllWindows()
    pygame.quit()
