import cv2
import time


class Camara:

    def __init__(self, indice=0, ancho=1280, alto=720):
        self.indice = indice
        self.camara = None
        self.ancho = ancho
        self.alto = alto
        self.tiempo_anterior = 0

    def abrir(self):
        print("Iniciando cámara...")
        self.camara = cv2.VideoCapture(self.indice)

        if not self.camara.isOpened():
            print("ERROR: No se pudo abrir la cámara")
            return False

        self.camara.set(cv2.CAP_PROP_FRAME_WIDTH, self.ancho)
        self.camara.set(cv2.CAP_PROP_FRAME_HEIGHT, self.alto)
        print("Cámara abierta correctamente")
        return True

    def leer(self):
        if self.camara is None:
            return False, None
        return self.camara.read()

    def mostrar_fps(self, frame):
        tiempo_actual = time.time()
        delta = tiempo_actual - self.tiempo_anterior
        fps = 1 / delta if delta > 0 else 0
        self.tiempo_anterior = tiempo_actual

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (30, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )
        return frame

    def cerrar(self):
        if self.camara is not None:
            self.camara.release()