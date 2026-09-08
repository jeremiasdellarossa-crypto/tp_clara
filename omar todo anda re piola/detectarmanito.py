import cv2
import mediapipe as mp
import os
import math


class detectormano:

    def __init__(self):

        carpeta = os.path.dirname(os.path.abspath(__file__))
        modelo = os.path.join(carpeta, "hand_landmarker.task")

        print("🧠 Buscando modelo...")
        print("📁 Ruta:", modelo)

        if not os.path.exists(modelo):
            raise FileNotFoundError(
                f"No se encontró el modelo en: {modelo}"
            )

        opciones = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=modelo
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=2
        )

        self.detector = (
            mp.tasks.vision.HandLandmarker.create_from_options(
                opciones
            )
        )

        self.timestamp = 0

        print("🟢 Detector de manos iniciado correctamente")

    # -----------------------------------
    # DETECTAR MANO
    # -----------------------------------

    def detectar(self, frame):

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        imagen = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )

        self.timestamp += 1

        resultado = self.detector.detect_for_video(
            imagen,
            self.timestamp
        )

        return resultado

    # -----------------------------------
    # CONTAR DEDOS
    # -----------------------------------

    def contar_dedos(self, landmarks):

        dedos = 0

    # -------------------------
    # ÍNDICE, MEDIO, ANULAR
    # Y MEÑIQUE
    # -------------------------

        dedos_largos = [
            (8, 6),     # Índice
            (12, 10),   # Medio
            (16, 14),   # Anular
            (20, 18)    # Meñique
        ]

        for punta, articulacion in dedos_largos:

            if landmarks[punta].y < landmarks[articulacion].y:
                dedos += 1

    # -------------------------
    # PULGAR
    # -------------------------

    # Distancia desde el pulgar hasta la muñeca
        distancia_pulgar = math.dist(
        (landmarks[4].x, landmarks[4].y),
        (landmarks[0].x, landmarks[0].y)
        )

    # Distancia desde la articulación del pulgar
    # hasta la muñeca
        distancia_articulacion = math.dist(
        (landmarks[3].x, landmarks[3].y),
        (landmarks[0].x, landmarks[0].y)
        )

    # Si la punta está bastante más lejos de la muñeca,
    # consideramos que el pulgar está extendido.
        if distancia_pulgar > distancia_articulacion * 1.15:
            dedos += 1

        return dedos
    # -----------------------------------
    # DETECTAR GESTO
    # -----------------------------------

    def detectar_gesto(self, resultado):

        if not resultado.hand_landmarks:
            return "Sin mano"

        landmarks = resultado.hand_landmarks[0]

        dedos = self.contar_dedos(landmarks)

        if dedos == 0:
            return "Puño"

        elif dedos == 1:
            return "1 dedo"

        elif dedos == 2:
            return "2 dedos"

        elif dedos == 3:
            return "3 dedos"

        elif dedos == 4:
            return "4 dedos"

        elif dedos == 5:
            return "Mano abierta"

        return "Gesto desconocido"

    # -----------------------------------
    # DIBUJAR MANO
    # -----------------------------------

    def dibujar(self, frame, resultado):

        conexiones = [
            # Pulgar
            (0, 1), (1, 2), (2, 3), (3, 4),

            # Índice
            (0, 5), (5, 6), (6, 7), (7, 8),

            # Medio
            (0, 9), (9, 10), (10, 11), (11, 12),

            # Anular
            (0, 13), (13, 14), (14, 15), (15, 16),

            # Meñique
            (0, 17), (17, 18), (18, 19), (19, 20),

            # Palma
            (5, 9),
            (9, 13),
            (13, 17)
        ]

        if resultado.hand_landmarks:

            alto, ancho, _ = frame.shape

            for landmarks in resultado.hand_landmarks:

                puntos = []

                for landmark in landmarks:

                    x = int(landmark.x * ancho)
                    y = int(landmark.y * alto)

                    puntos.append((x, y))

                # Dibujar líneas
                for inicio, fin in conexiones:

                    cv2.line(
                        frame,
                        puntos[inicio],
                        puntos[fin],
                        (0, 255, 0),
                        2
                    )

                # Dibujar puntos
                for x, y in puntos:

                    cv2.circle(
                        frame,
                        (x, y),
                        5,
                        (0, 255, 0),
                        -1
                    )

        return frame

    # -----------------------------------
    # CERRAR
    # -----------------------------------

    def cerrar(self):

        self.detector.close()

        print("🔴 Detector de manos cerrado")