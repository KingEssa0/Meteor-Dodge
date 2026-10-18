import pygame
import sys
import random
import os

pygame.init()

WIDTH, HEIGHT = 900, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
GAME_WIDTH, GAME_HEIGHT = 300, 200
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Meteor Dodge")

clock = pygame.time.Clock()

def draw_text_panel(rect, color=(5, 12, 28, 210)):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill(color)
    screen.blit(panel, rect.topleft)


def draw_screen_text(text, font, color, center):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center)
    screen.blit(text_surface, text_rect)


BLACK = (10, 10, 20)
BLUE = (50, 160, 255)
ORANGE = (255, 120, 40)
DARK_ORANGE = (190, 65, 25)
WHITE = (255, 255, 255)
RED = (255, 70, 70)

font = pygame.font.Font(None, 30)
big_font = pygame.font.Font(None, 64)

menu_font = pygame.font.Font(None, 76)
subtitle_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

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
fire_particles = []
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

if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as file:
        try:
            high_score = int(file.read())
        except ValueError:
            high_score = 0
else:
    high_score = 0

playing = False
game_started = False


running = True

while running:
    dt = clock.tick(FPS) / 1000

    if playing:
        survival_time += dt

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_started:
                    playing = True
                    game_started = True
                elif playing:
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

            if game_started and not playing and event.key == pygame.K_r:
                player.x = GAME_WIDTH // 2 - PLAYER_WIDTH // 2
                player.y = GAME_HEIGHT - 30
                meteors.clear()
                lasers.clear()
                particles.clear()
                spawn_timer = 0
                survival_time = 0
                playing = True
                game_started = True

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

            meteor_base_image = pygame.transform.scale(
                pygame.image.load("assets/meteor.png").convert_alpha(),
                (size, size)
            )

            meteors.append({
                "rect": pygame.Rect(x, -size, size, size),
                "x": x + size / 2,
                "y": float(-size),
                "size": size,
                "speed": speed,
                "base_image": meteor_base_image,
                "image": meteor_base_image,
                "mask": pygame.mask.from_surface(meteor_base_image),
                "angle":random.uniform(0, 360),
                "rotation_speed": random.choice([-1, 1]) * random.randint(100, 240)
            })

        for laser in lasers:
            laser.y -= int(LASER_SPEED * dt)

        lasers  = [laser for laser in lasers if laser.bottom > 0]

        for meteor in meteors:
            meteor["y"] += meteor["speed"] * dt

            meteor["angle"] = (
                meteor["angle"] + meteor["rotation_speed"] * dt
            ) % 360

            rotated_image = pygame.transform.rotate(
                meteor["base_image"],
                meteor["angle"]
            )

            meteor["rect"] = rotated_image.get_rect(
                center=(
                    round(meteor["x"]),
                    round(meteor["y"] + meteor["size"] / 2)
                )
            )

            meteor["image"] = rotated_image
            meteor["mask"] = pygame.mask.from_surface(rotated_image)

            if random.random() < 0.8:
                trail_length = random.uniform(8, 24)
                side = random.choice([-1, 1])

                fire_particles.append({
                    "x": meteor["x"] + side * trail_length * 0.35
                        + random.uniform(-2, 2),
                    "y": meteor["y"] + random.uniform(0, meteor["size"] / 2),
                    "vx": side * random.uniform(5, 25),
                    "vy": random.uniform(-45, -15),
                    "life": random.uniform(0.15, 0.35),
                    "size": random.randint(1, 3),
                    "color": random.choice([
                        (255, 220, 80),
                        (255, 140, 30),
                        (255, 65, 30),
                        (190, 45, 25)
                    ])
                })
            if player.colliderect(meteor["rect"]):
                offset = (
                    meteor["rect"].x - player.x,
                    meteor["rect"].y - player.y
                )

                if ship_mask.overlap(meteor["mask"], offset):
                    playing = False
                    lasers.clear()
                    break


            if player.colliderect(meteor["rect"]):
                offset = (
                    meteor["rect"].x - player.x,
                    meteor["rect"].y - player.y
                )

                if ship_mask.overlap(meteor["mask"], offset):
                    playing = False
                    lasers.clear()
                    break

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

                    break

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

    if game_started:
        game_surface.blit(ship_img, player)

    if playing:
        for laser in lasers:
            pygame.draw.rect(game_surface, (0, 255, 255), laser)

    for particle in particles:
        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt
        particle["life"] -= dt

    for particle in fire_particles:
        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt
        particle["life"] -= dt

    fire_particles = [
        particle for particle in fire_particles
        if particle["life"] > 0
    ]

    particles = [
        p for p in particles
        if p["life"] > 0
    ]

    for particle in fire_particles:
        pygame.draw.circle(
            game_surface,
            particle["color"],
            (int(particle["x"]), int(particle["y"])),
            particle["size"]
        )

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

    if score > high_score:
        high_score = score

        with open("highscore.txt", "w") as file:
            file.write(str(high_score))




    pixel_frame = pygame.transform.scale(
        game_surface,
        (WIDTH, HEIGHT)
    )
    screen.blit(pixel_frame, (0, 0))

    if playing:
        draw_screen_text(
            f"Score: {score}",
            subtitle_font,
            WHITE,
            (100, 30)
        )

        draw_screen_text(
            f"Best: {high_score}",
            subtitle_font,
            WHITE,
            (100, 65)
        )

    if game_started and not playing:
        draw_screen_text(
            "GAME OVER",
            pygame.font.Font(None, 96),
            RED,
            (WIDTH // 2, 245)
        )

        draw_screen_text(
            f"Score: {score}",
            subtitle_font,
            WHITE,
            (WIDTH // 2, 320)
        )

        draw_screen_text(
            "Press R to restart | ESC to quit",
            subtitle_font,
            WHITE,
            (WIDTH // 2, 370)
        )

    if not game_started:
        draw_text_panel(
            pygame.Rect(100, 105, 700, 370)
        )

        draw_screen_text(
            "METEOR DODGE",
            menu_font,
            BLUE,
            (WIDTH // 2, 165)
        )

        draw_screen_text(
            "Press SPACE to start",
            subtitle_font,
            WHITE,
            (WIDTH // 2, 280)
        )

        draw_screen_text(
            "Move: A/D or arrow keys",
            subtitle_font,
            WHITE,
            (WIDTH // 2, 355)
        )

        draw_screen_text(
            "Shoot: SPACE",
            subtitle_font,
            ORANGE,
            (WIDTH // 2, 410)
        )

    pygame.display.flip()

pygame.quit()
sys.exit()