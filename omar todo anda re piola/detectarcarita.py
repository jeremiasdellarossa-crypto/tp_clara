import cv2
import mediapipe as mp
import os


class DetectorCara:

    def __init__(self):
        carpeta = os.path.dirname(os.path.abspath(__file__))
        modelo = os.path.join(carpeta, "face_landmarker.task")

        print("Buscando modelo de cara...")
        if not os.path.exists(modelo):
            raise FileNotFoundError(f"No se encontró el modelo en: {modelo}")

        opciones = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=modelo),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_faces=1,
            output_face_blendshapes=True  
        )

        self.detector = mp.tasks.vision.FaceLandmarker.create_from_options(opciones)
        self.timestamp = 0
        print("Detector de cara iniciado correctamente")

    def detectar(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        self.timestamp += 1
        return self.detector.detect_for_video(imagen, self.timestamp)

    def detectar_expresion(self, resultado):
        if not resultado.face_blendshapes:
            return "Neutral"

        blendshapes = resultado.face_blendshapes[0]
        
        expresiones = {b.category_name: b.score for b in blendshapes}

        sonrisa_izq = expresiones.get("mouthSmileLeft", 0.0)
        sonrisa_der = expresiones.get("mouthSmileRight", 0.0)
        promedio_sonrisa = (sonrisa_izq + sonrisa_der) / 2.0

        fruncir_ceño = expresiones.get("browDownLeft", 0.0) + expresiones.get("browDownRight", 0.0)

        if promedio_sonrisa > 0.45:
            return "Sonriendo"
        elif fruncir_ceño > 0.6:
            return "Enojado"
        
        return "Neutral"

    def dibujar(self, frame, resultado):
        if resultado.face_landmarks:
            alto, ancho, _ = frame.shape
            for face_landmarks in resultado.face_landmarks:
                for landmark in face_landmarks:
                    x = int(landmark.x * ancho)
                    y = int(landmark.y * alto)
                    cv2.circle(frame, (x, y), 1, (255, 0, 0), -1)

        return frame

    def cerrar(self):
        self.detector.close()
        print("Detector de cara cerrado")