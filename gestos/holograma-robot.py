import cv2
import pygame
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import gestos
    USAR_GESTOS = True
except ImportError:
    import mediapipe as mp
    USAR_GESTOS = False


pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HOLO-AI / HOLO-SIGN - Control por Cámara")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
BLUE_ROBOT = (0, 150, 255)
WHITE = (255, 255, 255)


cap = cv2.VideoCapture(0)
font = pygame.font.SysFont("Arial", 20)

if not USAR_GESTOS:
    try:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.6)
    except AttributeError:
        import mediapipe.python.solutions.hands as mp_hands
        hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.6)


cx = WIDTH // 2
cy = HEIGHT // 2 + 20

wave_angle = 0
wave_dir = 1
crouch_offset = 0


jump_offset = 0
is_jumping = False
jump_speed = 14
gravity = 1


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    ret, frame = cap.read()
    action = "IDLE"

    if ret:
        frame = cv2.flip(frame, 1)

    
        if USAR_GESTOS and hasattr(gestos, 'procesar_frame'):
            action = gestos.procesar_frame(frame)
        elif USAR_GESTOS and hasattr(gestos, 'detectar_gesto'):
            action = gestos.detectar_gesto(frame)
        else:
            # Detección directa si gestos.py no responde
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    hy = hand_landmarks.landmark[9].y
                    hx = hand_landmarks.landmark[9].x

                    if hy < 0.25:
                        action = "SALTAR"
                    elif hy < 0.45:
                        action = "SALUDAR"
                    elif hy > 0.75:
                        action = "AGACHARSE"
                    elif hx < 0.3:
                        action = "MOVER_IZQ"
                    elif hx > 0.7:
                        action = "MOVER_DER"

    
    action_str = str(action).upper() if action else "IDLE"

    
    
       
    if action_str == "SALUDAR":
        wave_angle += 5 * wave_dir
        if wave_angle > 25 or wave_angle < -25: wave_dir *= -1
    else:
        wave_angle = 0

    
    if action_str == "AGACHARSE":
        if crouch_offset < 35: crouch_offset += 4
    else:
        if crouch_offset > 0: crouch_offset -= 4

    
    if action_str == "SALTAR" and not is_jumping:
        is_jumping = True
        jump_speed = 14

    if is_jumping:
        jump_offset -= jump_speed
        jump_speed -= gravity
        if jump_offset >= 0:
            jump_offset = 0
            is_jumping = False

    
    if action_str == "MOVER_IZQ" and cx > 200:
        cx -= 6
    elif action_str == "MOVER_DER" and cx < WIDTH - 200:
        cx += 6

    
    screen.fill(BLACK)
    current_y = cy + crouch_offset + jump_offset

    
    pygame.draw.circle(screen, BLUE_ROBOT, (cx, current_y - 120), 40)
    pygame.draw.circle(screen, BLACK, (cx - 15, current_y - 125), 6)
    pygame.draw.circle(screen, BLACK, (cx + 15, current_y - 125), 6)

    
    torso_height = 90 - crouch_offset
    pygame.draw.rect(screen, BLUE_ROBOT, (cx - 35, current_y - 70, 70, torso_height), border_radius=10)
    pygame.draw.circle(screen, WHITE, (cx, current_y - 25), 10)

    
    pygame.draw.line(screen, BLUE_ROBOT, (cx - 35, current_y - 60), (cx - 60, current_y - 10), 12)

    
    if action_str == "SALUDAR":
        hand_x = cx + 60 + wave_angle
        hand_y = current_y - 100
        pygame.draw.line(screen, BLUE_ROBOT, (cx + 35, current_y - 60), (hand_x, hand_y), 12)
        pygame.draw.circle(screen, BLUE_ROBOT, (hand_x, hand_y), 10)
    else:
        pygame.draw.line(screen, BLUE_ROBOT, (cx + 35, current_y - 60), (cx + 60, current_y - 10), 12)

    
    leg_height = max(10, 50 - crouch_offset)
    pygame.draw.rect(screen, BLUE_ROBOT, (cx - 25, current_y + 20 - crouch_offset, 18, leg_height), border_radius=5)
    pygame.draw.rect(screen, BLUE_ROBOT, (cx + 7, current_y + 20 - crouch_offset, 18, leg_height), border_radius=5)

    
    txt_display = "SALTANDO" if is_jumping else action_str
    txt = font.render(f"DETECCION CÁMARA: {txt_display}", True, BLUE_ROBOT if txt_display != "IDLE" else WHITE)
    screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()
sys.exit()