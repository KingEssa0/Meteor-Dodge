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

ship_img = pygame.image.load("assets/ship.png").convert_alpha()
ship_img = pygame.transform.scale(ship_img, (75, 75))

meteor_img = pygame.image.load("assets/meteor.png").convert_alpha()
meteor_img = pygame.transform.scale(meteor_img, (45, 45))
background_img = pygame.image.load("assets/background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))


PLAYER_WIDTH = 75
PLAYER_HEIGHT = 75
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
lasers = []
LASER_SPEED = 500
stars = [
    [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)]
    for _ in range(80)
]
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and playing:
                laser = pygame.Rect(
                    player.centerx - 3,
                    player.top,
                    6,
                    20
                )
                lasers.append(laser)
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

        spawn_interval = max(0.2, METEOR_SPAWN_INTERVAL - survival_time * 0.01)
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            meteor_type = random.choice(["small", "normal", "large"])

            if meteor_type == "small":
                size = 20
                speed = random.randint(300, 450)

            elif meteor_type == "large":
                size = 45
                speed = random.randint(140, 240)
            else:
                size = 32
                speed = random.randint(200, 350)

            speed += int(survival_time * 5)
            x = random.randint(0, WIDTH - size)

            meteors.append({
                "rect": pygame.Rect(x, -size, size, size),
                "speed": speed
            })

        for meteor in meteors:
            meteor["rect"].y += int(meteor["speed"] * dt)

            for laser in lasers:
                laser.y -= int(LASER_SPEED * dt)

            lasers  = [laser for laser in lasers if laser.bottom > 0]

            if player.colliderect(meteor["rect"]):
                playing = False

        remaining_meteors = []

        for meteor in meteors:
            hit = False

            for laser in lasers:
                if laser.colliderect(meteor["rect"]):
                    hit = True
                    lasers.remove(laser)
                    break

            if not hit:
                remaining_meteors.append(meteor)

        meteors = [
            m for m in remaining_meteors
            if m["rect"].top < HEIGHT
        ]


    screen.blit(background_img, (0, 0))
    if playing:
        for star in stars:
            star[1] += star[2]

            if star[1] > HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, WIDTH)

            pygame.draw.circle(
                screen,
                WHITE,
                (star[0], star[1]),
                star[2] //2 + 1
            )
    else:
        for star in stars:
            pygame.draw.circle(
                screen,
                WHITE,
                (star[0], star[1]),
                star[2] //2 + 1
            )

    screen.blit(ship_img, player)

    for laser in lasers:
        pygame.draw.rect(screen, (0, 255, 255), laser)

    for meteor in meteors:
        image = pygame.transform.scale(
            meteor_img,
            (meteor["rect"].width, meteor["rect"].height)
        )
        screen.blit(image, meteor["rect"])

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