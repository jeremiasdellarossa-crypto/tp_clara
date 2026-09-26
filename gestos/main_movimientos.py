import pygame
from gesto import Mercedes

pygame.init()

pantalla = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Mercedes - Movimiento")

reloj = pygame.time.Clock()

mercedes = Mercedes()

ejecutando = True

while ejecutando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_LEFT:
                mercedes.izquierda()

            elif evento.key == pygame.K_RIGHT:
                mercedes.derecha()

            elif evento.key == pygame.K_UP:
                mercedes.arriba()

            elif evento.key == pygame.K_DOWN:
                mercedes.abajo()

            elif evento.key == pygame.K_SPACE:
                mercedes.saltar()

            elif evento.key == pygame.K_a:
                mercedes.agacharse()

            elif evento.key == pygame.K_s:
                mercedes.saludar()

            elif evento.key == pygame.K_ESCAPE:
                ejecutando = False

    pantalla.fill((0, 0, 0))

    pygame.draw.circle(
        pantalla,
        (255, 255, 255),
        (mercedes.x, mercedes.y),
        40
    )

    pygame.display.flip()

    reloj.tick(60)

pygame.quit()