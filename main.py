import math
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


def add_popup(x,  y, text, color=(255, 255, 80)):
    score_popups.append({
        "x": float(x),
        "y": float(y),
        "text": text,
        "color": color,
        "life": 0.8
    })


def create_particles(x, y, count, colors, speed=80):
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        velocity = random.uniform(speed * 0.3, speed)


        particles.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(angle) * velocity,
            "vy": math.sin(angle) * velocity,
            "life": random.uniform(0.25, 0.65),
            "size": random.randint(1, 3),
            "color": random.choice(colors),
        })


def save_progress():
    with open("highscore.txt", "w") as file:
        file.write(str(high_score))

    with open("unlocked_ships.txt", "w") as file:
        file.write(",".join(map(str, unlocked_ships)))


BLACK = (10, 10, 20)
BLUE = (50, 160, 255)
ORANGE = (255, 120, 40)
DARK_ORANGE = (190, 65, 25)
WHITE = (255, 255, 255)
RED = (255, 70, 70)
YELLOW = (255, 255, 80)
CYAN = (0, 255, 255)
GREEN = (70, 255, 130)
PURPLE = (190, 100, 255)

font = pygame.font.Font(None, 30)
big_font = pygame.font.Font(None, 64)

menu_font = pygame.font.Font(None, 76)
subtitle_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

ship_img = pygame.image.load("assets/ship.png").convert_alpha()
ship_img = pygame.transform.scale(ship_img, (25, 25))
ship_mask = pygame.mask.from_surface(ship_img)

meteor_original = pygame.image.load(
    "assets/meteor.png"
).convert_alpha()

meteor_original = pygame.transform.scale(
    meteor_original, (45, 45)
)
background_img = pygame.image.load("assets/background.png").convert()
background_img = pygame.transform.scale(
    background_img, (GAME_WIDTH, GAME_HEIGHT)
)

start_screen_img = pygame.image.load(
    "assets/start_screen.png"
).convert()

start_screen_img = pygame.transform.scale(
    start_screen_img, (WIDTH, HEIGHT)
)

game_over_img = pygame.image.load(
    "assets/game_over.png"
).convert()

game_over_img = pygame.transform.scale(
    game_over_img, (WIDTH, HEIGHT)
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

destroy_score = 0
combo = 0
combo_timer = 0
COMBO_WINDOW = 2.0

METEOR_POINTS = {
    7: 10,
    11: 25,
    15: 50
}

score_popups = []
powerups = []
active_powerups = {
    "rapid": 0,
    "shield": 0,
    "slow": 0
}

laser_cooldown = 0

LASER_NORMAL_COOLDOWN = 0.3
LASER_RAPID_COOLDOWN = 0.09

ship_options = [
    {"name": "STANDARD", "speed": 133, "laser": 0.3,
     "unlock": 0},
    {"name": "SPEEDSTER", "speed": 175, "laser": 0.3,
     "unlock": 500},
    {"name": "RAPID", "speed": 120, "laser": 0.18,
     "unlock": 1200}
]

selected_ship = 0
unlocked_ships = [0]

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

death_animation = False
death_timer = 0
DEATH_ANIMATION_DURATION = 1.0
GAME_OVER_FADE_DURATION = 0.6
game_over_fade = 0

fade_overlay = pygame.Surface((WIDTH, HEIGHT))
fade_overlay.fill((0, 0, 0))
running = True

while running:
    dt = clock.tick(FPS) / 1000
    if death_animation:
        death_timer += dt

        if death_timer >= DEATH_ANIMATION_DURATION:
            death_animation = False
            game_over_fade = 0
            fire_particles.clear()
            meteors.clear()

    if playing:
        survival_time += dt

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not game_started:
                    playing = True
                    game_started = True

            if event.key == pygame.K_SPACE and playing:
                if laser_cooldown <= 0:
                    laser = pygame.Rect(
                        player.centerx - 1,
                        player.top,
                        2,
                        7
                    )
                    lasers.append(laser)

                    if active_powerups["rapid"] > 0:
                        laser_cooldown = LASER_RAPID_COOLDOWN
                    else:
                        laser_cooldown = ship_options[selected_ship]["laser"]
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
                fire_particles.clear()

                death_animation = False
                death_timer = 0
                game_over_fade = 0

                spawn_timer = 0
                survival_time = 0
                destroy_score = 0
                combo = 0
                combo_timer = 0
                score_popups.clear()
                powerups.clear()

                for power in active_powerups:
                    active_powerups[power] = 0
                playing = True
                game_started = True

    keys = pygame.key.get_pressed()

    if playing:
        PLAYER_SPEED = ship_options[selected_ship]["speed"]

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= int(PLAYER_SPEED * dt)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += int(PLAYER_SPEED * dt)

    player.left = max(0, player.left)
    player.right = min(GAME_WIDTH, player.right)

    if playing:
        spawn_timer += dt
        laser_cooldown = max(0, laser_cooldown - dt)

        for power in active_powerups:
            active_powerups[power] = max(
                0, active_powerups[power] - dt
            )

        if combo_timer > 0:
            combo_timer -= dt
        else:
            combo = 0

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
                meteor_original,
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
                    for _ in range(45):
                        particles.append({
                            "x": player.centerx,
                            "y": player.centery,
                            "vx": random.uniform(-100, 100),
                            "vy": random.uniform(-100, 100),
                            "life": random.uniform(0.4, 1.0),
                            "size": random.randint(1, 4),
                            "color": random.choice([
                                (255, 255, 255),
                                (255, 220, 80),
                                (255, 140, 30),
                                (255, 65, 30),
                                (80, 180, 255)
                            ])
                        })

                    playing = False
                    death_animation = True
                    death_timer = 0
                    lasers.clear()
                    break

        remaining_meteors = []
        lasers_to_remove = []

        for meteor in meteors:
            if not playing:
                break

            hit = False

            for laser in lasers:
                if laser.colliderect(meteor["rect"]):
                    hit = True
                    lasers_to_remove.append(laser)

                    points = METEOR_POINTS.get(meteor["size"], 10)

                    if combo_timer > 0:
                        combo += 1
                    else:
                        combo = 1

                    combo_timer = COMBO_WINDOW

                    multiplier = min(5, combo)
                    earned_points = points * multiplier
                    destroy_score += earned_points

                    add_popup(
                        meteor["rect"].centerx,
                        meteor["rect"].centery,
                        f"+{earned_points} x{multiplier}",
                        YELLOW if multiplier < 3 else CYAN
                    )

                    fragment_count = 8 if meteor["size"] <= 7 else 16
                    create_particles(
                        meteor["rect"].centerx,
                        meteor["rect"].centery,
                        fragment_count,
                        [ORANGE, DARK_ORANGE, RED, YELLOW, WHITE],
                        speed=100 if meteor["size"] <= 7 else 140
                    )

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

    if game_started and playing:
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

    for popup in score_popups:
        popup["y"] -= 25 * dt
        popup["life"] -= dt

        popup_surface = small_font.render(
            popup["text"],
            True,
            popup["color"]
        )

        game_surface.blit(
            popup_surface,
            (int(popup["x"]), int(popup["y"]))
        )

    score_popups = [
        popup for popup in score_popups
        if popup["life"] > 0
    ]


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

    score = int(survival_time) + destroy_score

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

        if combo >= 2:
            draw_screen_text(
                f"COMBO x{min(5, combo)}",
                small_font,
                CYAN,
                (100, 95)
            )

    if game_started and not playing and not death_animation:
        game_over_fade = min(
            255,
            game_over_fade + 255 * dt / GAME_OVER_FADE_DURATION
        )

        screen.blit(game_over_img, (0, 0))

        fade_overlay.set_alpha(int(255 - game_over_fade))
        screen.blit(fade_overlay, (0, 0))

    if not game_started:
        screen.blit(start_screen_img, (0, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()