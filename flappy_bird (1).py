
import pygame
import random

# Initialiser Pygame
pygame.init()

# Définir les dimensions de la fenêtre
screen_width = 400
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Charger les images
bird_image = pygame.image.load('bird.png')
background_image = pygame.image.load('background.png')
pipe_image = pygame.image.load('pipe.png')

# Définir les couleurs
WHITE = (255, 255, 255)

# Variables de l'oiseau
bird_x = 50
bird_y = screen_height // 2
bird_y_change = 0

# Variables des tuyaux
pipe_width = 70
pipe_height = random.randint(150, 450)
pipe_x = screen_width
pipe_gap = 200

# Variables de score
score = 0
font = pygame.font.Font(None, 36)

# Boucle principale du jeu
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_y_change = -6
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                bird_y_change = 3

    # Mise à jour de la position de l'oiseau
    bird_y += bird_y_change

    # Déplacement des tuyaux
    pipe_x -= 3
    if pipe_x < -pipe_width:
        pipe_x = screen_width
        pipe_height = random.randint(150, 450)
        score += 1

    # Collision avec le sol ou le plafond
    if bird_y > screen_height or bird_y < 0:
        running = False

    # Collision avec les tuyaux
    if bird_x + bird_image.get_width() > pipe_x and bird_x < pipe_x + pipe_width:
        if bird_y < pipe_height or bird_y + bird_image.get_height() > pipe_height + pipe_gap:
            running = False

    # Afficher l'arrière-plan
    screen.blit(background_image, (0, 0))

    # Afficher les tuyaux
    screen.blit(pipe_image, (pipe_x, pipe_height - pipe_image.get_height()))
    screen.blit(pipe_image, (pipe_x, pipe_height + pipe_gap), pygame.Rect(0, 0, pipe_width, screen_height))

    # Afficher l'oiseau
    screen.blit(bird_image, (bird_x, bird_y))

    # Afficher le score
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(30)

pygame.quit()
