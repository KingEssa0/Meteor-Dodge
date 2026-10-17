import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 900, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
GAME_WIDTH, GAME_HEIGHT = 300, 200
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Meteor Dodge")

clock = pygame.time.Clock()

BLACK = (10, 10, 20)
BLUE = (50, 160, 255)
ORANGE = (255, 120, 40)
DARK_ORANGE = (190, 65, 25)
WHITE = (255, 255, 255)
RED = (255, 70, 70)

font = pygame.font.Font(None, 12)
big_font = pygame.font.Font(None, 24)

ship_img = pygame.image.load("assets/ship.png").convert_alpha()
ship_img = pygame.transform.scale(ship_img, (25, 25))
ship_mask = pygame.mask.from_surface(ship_img)

meteor_img = pygame.image.load("assets/meteor.png").convert_alpha()
meteor_img = pygame.transform.scale(meteor_img, (45, 45))
meteor_mask = pygame.mask.from_surface(meteor_img)
background_img = pygame.image.load("assets/background.png").convert()
background_img = pygame.transform.scale(
    background_img, (GAME_WIDTH, GAME_HEIGHT)
)


PLAYER_WIDTH = 25
PLAYER_HEIGHT = 25
PLAYER_SPEED = 133

METEOR_MIN_SIZE = 20
METEOR_MAX_SIZE = 45
METEOR_SPAWN_INTERVAL = 0.7

player_x = GAME_WIDTH // 2 - PLAYER_WIDTH // 2
player_y = GAME_HEIGHT - 30

player = pygame.Rect(
    player_x,
    player_y,
    PLAYER_WIDTH,
    PLAYER_HEIGHT
)

meteors = []
lasers = []
LASER_SPEED = 167
particles = []
stars = [
    [
        random.randint(0, GAME_WIDTH - 1),
        random.randint(0, GAME_HEIGHT - 1),
        random.randint(1, 2)
     ]
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
                    player.centerx - 1,
                    player.top,
                    2,
                    7
                )
                lasers.append(laser)
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if not playing and event.key == pygame.K_r:
                player.x = GAME_WIDTH // 2 - PLAYER_WIDTH // 2
                meteors.clear()
                lasers.clear()
                particles.clear()
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
    player.right = min(GAME_WIDTH, player.right)

    if playing:
        spawn_timer += dt

        spawn_interval = max(0.2, METEOR_SPAWN_INTERVAL - survival_time * 0.01)
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            meteor_type = random.choice(["small", "normal", "large"])

            if meteor_type == "small":
                size = 7
                speed = random.randint(100, 150)

            elif meteor_type == "large":
                size = 15
                speed = random.randint(47, 80)
            else:
                size = 11
                speed = random.randint(67, 117)

            speed += int(survival_time * 2)
            x = random.randint(0, GAME_WIDTH - size)

            meteor_image = pygame.transform.scale(
                pygame.image.load("assets/meteor.png").convert_alpha(),
                (size, size)
            )

            meteor_mask = pygame.mask.from_surface(meteor_image)

            meteors.append({
                "rect": pygame.Rect(x, -size, size, size),
                "speed": speed,
                "image": meteor_image,
                "mask": meteor_mask
            })

        for laser in lasers:
            laser.y -= int(LASER_SPEED * dt)

        lasers  = [laser for laser in lasers if laser.bottom > 0]

        for meteor in meteors:
            meteor["rect"].y += int(meteor["speed"] * dt)


            if player.colliderect(meteor["rect"]):
                offset = (
                    meteor["rect"].x - player.x,
                    meteor["rect"].y - player.y
                )

                if ship_mask.overlap(meteor["mask"], offset):
                    playing = False

        remaining_meteors = []
        lasers_to_remove = []

        for meteor in meteors:
            hit = False

            for laser in lasers:
                if laser.colliderect(meteor["rect"]):
                    hit = True
                    lasers_to_remove.append(laser)

                    for _ in range(12):
                        particles.append({
                            "x": meteor["rect"].centerx,
                            "y": meteor["rect"].centery,
                            "vx": random.uniform(-60, 60),
                            "vy": random.uniform(-60, 60),
                            "life": random.uniform(0.2, 0.5),
                            "size": random.randint(1, 3),
                            "color": random.choice([
                                ORANGE, DARK_ORANGE, RED, WHITE
                            ])
                        })

            if not hit:
                remaining_meteors.append(meteor)

        meteors = remaining_meteors

        lasers = [
            laser for laser in lasers
            if laser not in lasers_to_remove
        ]

    game_surface.blit(background_img, (0, 0))
    if playing:
        for star in stars:
            star[1] += star[2]

            if star[1] > GAME_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, GAME_WIDTH - 1)

            pygame.draw.rect(
                game_surface,
                WHITE,
                (star[0], star[1], star[2], star[2]),
            )
    else:
        for star in stars:
            pygame.draw.circle(
                game_surface,
                WHITE,
                (star[0], star[1]),
                star[2] //2 + 1
            )

    game_surface.blit(ship_img, player)

    for laser in lasers:
        pygame.draw.rect(game_surface, (0, 255, 255), laser)

    for particle in particles:
        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt
        particle["life"] -= dt

    particles = [
        p for p in particles
        if p["life"] > 0
    ]

    for meteor in meteors:
        game_surface.blit(meteor["image"], meteor["rect"])

    for particle in particles:
        pygame.draw.rect(
            game_surface,
            particle["color"],
            (
                int(particle["x"]),
                int(particle["y"]),
                particle["size"],
                particle["size"]
            )
        )

    score = int(survival_time)
    high_score = max(high_score, score)

    score_text = font.render(
        f"Score: {score}", True, WHITE
    )
    game_surface.blit(score_text, (7, 7))
    best_text = font.render(f"Best: {high_score}", True, WHITE)
    game_surface.blit(best_text, (7, 20))

    if not playing:
        title = big_font.render(
            "GAME OVER", True, RED
        )
        restart = font.render(
            "Press R to restart | ESC to quit", True, WHITE
        )
        game_surface.blit(
            title,
            title.get_rect(
                center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 30)
            )
        )
        game_surface.blit(
            restart,
            restart.get_rect(
                center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 40)
            )
        )

    pixel_frame = pygame.transform.scale(
        game_surface, (WIDTH, HEIGHT)
    )
    screen.blit(pixel_frame, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()