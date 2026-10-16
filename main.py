import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 900, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Meteor Dodge")

clock = pygame.time.Clock()

BLACK = (10, 10, 20)
BLUE = (50, 160, 255)
ORANGE = (255, 120, 40)
DARK_ORANGE = (190, 65, 25)
WHITE = (255, 255, 255)
RED = (255, 70, 70)

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)


PLAYER_WIDTH = 40
PLAYER_HEIGHT = 30
PLAYER_SPEED = 400

METEOR_MIN_SIZE = 20
METEOR_MAX_SIZE = 45
METEOR_SPAWN_INTERVAL = 0.7

player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - 80

player = pygame.Rect(
    player_x,
    player_y,
    PLAYER_WIDTH,
    PLAYER_HEIGHT
)

meteors = []
spawn_timer = 0
survival_time = 0
high_score = 0
playing = True


running = True

while running:
    dt = clock.tick(FPS) / 1000

    if playing:
        survival_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if not playing and event.key == pygame.K_r:
                player.x = WIDTH // 2 - PLAYER_WIDTH // 2
                meteors.clear()
                spawn_timer = 0
                survival_time = 0
                playing = True

    keys = pygame.key.get_pressed()

    if playing:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= int(PLAYER_SPEED * dt)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += int(PLAYER_SPEED * dt)

    player.left = max(0, player.left)
    player.right = min(WIDTH, player.right)

    if playing:
        spawn_timer += dt

        if spawn_timer >= METEOR_SPAWN_INTERVAL:
            spawn_timer = 0
            size = random.randint(METEOR_MIN_SIZE, METEOR_MAX_SIZE)
            x = random.randint(0, WIDTH - size)

            meteors.append({
                "rect": pygame.Rect(x, -size, size, size),
                "speed": random.randint(180, 350) + int(survival_time * 3)
            })

        for meteor in meteors:
            meteor["rect"].y += int(meteor["speed"] * dt)

            if player.colliderect(meteor["rect"]):
                playing = False

        meteors = [m for m in meteors if m["rect"].top < HEIGHT]

    screen.fill(BLACK)

    pygame.draw.rect(
        screen,
        BLUE,
        player,
        border_radius=8
    )

    for meteor in meteors:
        pygame.draw.ellipse(
            screen,
            DARK_ORANGE,
            meteor["rect"]
        )

        pygame.draw.ellipse(
            screen,
            ORANGE,
            meteor["rect"].inflate(-6,-6)
        )

    score = int(survival_time)
    high_score = max(high_score, score)

    score_text = font.render(
        f"Score: {score}", True, WHITE
    )
    screen.blit(score_text, (20, 20))
    best_text = font.render(f"Best: {high_score}", True, WHITE)
    screen.blit(best_text, (20, 60))

    if not playing:
        title = big_font.render(
            "GAME OVER", True, RED
        )
        restart = font.render(
            "Press R to restart | ESC to quit", True, WHITE
        )
        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 - 30)
            )
        )
        screen.blit(
            restart,
            restart.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 40)
            )
        )

    pygame.display.flip()

pygame.quit()
sys.exit()