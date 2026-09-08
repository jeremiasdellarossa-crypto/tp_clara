import cv2

from camera import Camara
import detectarmanito


camara = Camara()
detector = detectarmanito.detectormano()


if not camara.abrir():
    exit()


print("Cámara funcionando")
print(" MediaPipe iniciado")
print(" Colocá una mano frente a la cámara")
print("Presioná Q para salir")


while True:

    ret, frame = camara.leer()

    if not ret:
        print("No se pudo leer el frame")
        break

    resultado = detector.detectar(frame)

    frame = detector.dibujar(frame, resultado)
   
    gesto = detector.detectar_gesto(resultado)
    
    if gesto == "MANO ABIERTA":
        accion = "ACTIVAR"

    elif gesto == "PUÑO":
        accion = "DETENER"

    elif gesto == "DOS DEDOS":
        accion = "CAMBIAR"

    elif gesto == "UN DEDO":
        accion = "SELECCIONAR"

    else:
        accion = ""

    cv2.putText(
        frame,
        gesto,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2)
    cv2.putText(
        frame,
        accion,
        (30, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2)
    cv2.imshow("HOLO-AI - Vision Artificial", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


detector.cerrar()
camara.cerrar()
cv2.destroyAllWindows()