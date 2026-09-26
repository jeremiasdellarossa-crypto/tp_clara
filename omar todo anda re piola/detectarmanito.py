import cv2
import mediapipe as mp
import os
import math


class detectormano:

    def __init__(self):
        carpeta = os.path.dirname(os.path.abspath(__file__))
        modelo = os.path.join(carpeta, "hand_landmarker.task")

        print("Buscando modelo...")
        print("Ruta:", modelo)

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

        print("Detector de manos iniciado correctamente")

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

    def contar_dedos(self, landmarks):
        dedos = 0

        dedos_largos = [
            (8, 5),    
            (12, 9),   
            (16, 13),  
            (20, 17) 
        ]

        for punta, base in dedos_largos:
            dist_punta = math.dist(
                (landmarks[punta].x, landmarks[punta].y),
                (landmarks[0].x, landmarks[0].y)
            )
            dist_base = math.dist(
                (landmarks[base].x, landmarks[base].y),
                (landmarks[0].x, landmarks[0].y)
            )

            if dist_punta > dist_base * 1.25:
                dedos += 1

        dist_pulgar = math.dist(
            (landmarks[4].x, landmarks[4].y),
            (landmarks[0].x, landmarks[0].y)
        )
        dist_articulacion = math.dist(
            (landmarks[3].x, landmarks[3].y),
            (landmarks[0].x, landmarks[0].y)
        )

        if dist_pulgar > dist_articulacion * 1.14:
            dedos += 1

        return dedos

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

    def dibujar(self, frame, resultado):
        conexions = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17)
        ]

        if resultado.hand_landmarks:
            alto, ancho, _ = frame.shape
            for landmarks in resultado.hand_landmarks:
                puntos = []
                for landmark in landmarks:
                    x = int(landmark.x * ancho)
                    y = int(landmark.y * alto)
                    puntos.append((x, y))

                for inicio, fin in conexions:
                    cv2.line(frame, puntos[inicio], puntos[fin], (0, 255, 0), 2)

                for x, y in puntos:
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        return frame

    def cerrar(self):
        self.detector.close()
        print("Detector de manos cerrado")