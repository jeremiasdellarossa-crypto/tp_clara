import cv2
from camera import Camara
import detectarmanito
import detectarcarita

camara = Camara()
detector_mano = detectarmanito.detectormano()
detector_cara = detectarcarita.DetectorCara()

if not camara.abrir():
    exit()

print("Cámara funcionando con mano, cara y expresiones")
print("Presioná Q para salir")

while True:
    ret, frame = camara.leer()

    if not ret:
        print("No se pudo leer el frame")
        break

    resultado_cara = detector_cara.detectar(frame)
    frame = detector_cara.dibujar(frame, resultado_cara)
    expresion_cara = detector_cara.detectar_expresion(resultado_cara)

    resultado_mano = detector_mano.detectar(frame)
    frame = detector_mano.dibujar(frame, resultado_mano)
    gesto_mano = detector_mano.detectar_gesto(resultado_mano)

    cv2.putText(frame, f"MANO: {gesto_mano}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"CARA: {expresion_cara}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    frame = camara.mostrar_fps(frame)

    cv2.imshow("HOLO-AI - Sistema Principal", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

detector_mano.cerrar()
detector_cara.cerrar()
camara.cerrar()
cv2.destroyAllWindows()