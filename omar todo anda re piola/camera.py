import cv2


class Camara:

    def __init__(self, indice=0):
        self.indice = indice
        self.camara = None

    def abrir(self):
        print("Iniciando cámara...")

        self.camara = cv2.VideoCapture(self.indice)

        if not self.camara.isOpened():
            print("❌ ERROR: No se pudo abrir la cámara")
            return False

        print("🟢 Cámara abierta correctamente")
        return True

    def leer(self):
        if self.camara is None:
            return False, None

        ret, frame = self.camara.read()

        if not ret:
            return False, None

        return True, frame

    def cerrar(self):
        if self.camara is not None:
            self.camara.release()
            print("🔴 Cámara cerrada")