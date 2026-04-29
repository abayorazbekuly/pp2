import pygame, sys
from pygame.locals import *
import random, time, json, os
from datetime import datetime

pygame.init()
pygame.mixer.init()

FPS = 60
FramePerSec = pygame.time.Clock()

RED   = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY  = (180, 180, 180)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

PLAYER_SPEED = 5
ENEMY_SPEED = 5
COIN_SPEED = 5

SCORE = 0
COIN_COUNT = 0

COINS_FOR_SPEEDUP = 5
next_speedup = COINS_FOR_SPEEDUP

DISTANCE = 0
FINISH_DISTANCE = 2000
POWER_BONUS = 0

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

SPRITES = {
    "background": "AnimatedStreet.png",
    "player": "Player.png",
    "enemy": "Enemy.png",
    "coin1": "Coin.png",
    "coin2": "Coins.png",
    "coin3": "MoreCoins.png",
    "barrier": "Barrier.png",
    "oil": "Oil.png",
    "pothole": "Pothole.png",
    "moving_barrier": "MovingBarrier.png",
    "speed_bump": "SpeedBump.png",
    "nitro_strip": "NitroStrip.png",
    "nitro": "Nitro.png",
    "shield": "Shield.png",
    "repair": "Repair.png"
}

font = pygame.font.SysFont("Verdana", 60)
font_medium = pygame.font.SysFont("Verdana", 30)
font_small = pygame.font.SysFont("Verdana", 20)
font_tiny = pygame.font.SysFont("Verdana", 15)

game_over_text = font.render("Game Over", True, BLACK)

background = pygame.image.load(SPRITES["background"])
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

crash_sound = pygame.mixer.Sound("crash.wav")

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer - TSIS 3")


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        file = open(SETTINGS_FILE, "r")
        data = json.load(file)
        file.close()
        return data

    return {
        "sound": True,
        "car_color": "default",
        "difficulty": "normal"
    }


def save_settings(settings):
    file = open(SETTINGS_FILE, "w")
    json.dump(settings, file, indent=4)
    file.close()


def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        file = open(LEADERBOARD_FILE, "r")
        data = json.load(file)
        file.close()
        return data

    return []


def save_leaderboard(data):
    data = sorted(data, key=lambda x: x["score"], reverse=True)
    data = data[:10]

    file = open(LEADERBOARD_FILE, "w")
    json.dump(data, file, indent=4)
    file.close()


def add_score_to_leaderboard(username, score, distance, coins):
    data = load_leaderboard()

    data.append({
        "name": username,
        "score": score,
        "distance": int(distance),
        "coins": coins,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    save_leaderboard(data)


def draw_text(text, font_obj, color, x, y):
    image = font_obj.render(text, True, color)
    DISPLAYSURF.blit(image, (x, y))


def draw_button(rect, text):
    pygame.draw.rect(DISPLAYSURF, WHITE, rect)
    pygame.draw.rect(DISPLAYSURF, BLACK, rect, 2)

    image = font_small.render(text, True, BLACK)
    DISPLAYSURF.blit(image, (rect.x + 20, rect.y + 12))


def tint_player(image, color_name):
    if color_name == "default":
        return image

    new_image = image.copy()

    if color_name == "red":
        color = (255, 0, 0, 60)
    elif color_name == "blue":
        color = (0, 0, 255, 60)
    elif color_name == "green":
        color = (0, 255, 0, 60)
    else:
        return image

    layer = pygame.Surface(new_image.get_size()).convert_alpha()
    layer.fill(color)
    new_image.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return new_image


def safe_x(player_rect):
    while True:
        x = random.randint(40, SCREEN_WIDTH - 40)

        if abs(x - player_rect.centerx) > 45:
            return x


def calculate_score():
    return SCORE * 5 + COIN_COUNT * 10 + int(DISTANCE / 5) + POWER_BONUS


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.image = pygame.image.load(SPRITES["enemy"]).convert_alpha()
        self.rect = self.image.get_rect()
        self.reset_position(player_rect)

    def reset_position(self, player_rect):
        self.rect.center = (safe_x(player_rect), random.randint(-700, -80))

    def move(self, player_rect):
        global SCORE
        self.rect.move_ip(0, ENEMY_SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset_position(player_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, settings):
        super().__init__()
        image = pygame.image.load(SPRITES["player"]).convert_alpha()
        self.image = tint_player(image, settings["car_color"])
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
        self.speed = PLAYER_SPEED

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)

        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)


class Coin(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.weight = 1
        self.image = None
        self.rect = None
        self.reset_position(player_rect)

    def load_coin_image(self):
        if self.weight == 1:
            self.image = pygame.image.load(SPRITES["coin1"]).convert_alpha()
        elif self.weight == 2:
            self.image = pygame.image.load(SPRITES["coin2"]).convert_alpha()
        else:
            self.image = pygame.image.load(SPRITES["coin3"]).convert_alpha()

        self.image = pygame.transform.smoothscale(self.image, (40, 40))

    def reset_position(self, player_rect):
        self.weight = random.randint(1, 3)
        self.load_coin_image()

        self.rect = self.image.get_rect()
        self.rect.center = (safe_x(player_rect), random.randint(-600, -50))

    def move(self, player_rect):
        self.rect.move_ip(0, COIN_SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position(player_rect)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.kind = random.choice(["barrier", "oil", "pothole"])
        self.image = None
        self.rect = None
        self.reset_position(player_rect)

    def load_image(self):
        self.image = pygame.image.load(SPRITES[self.kind]).convert_alpha()

        if self.kind == "barrier":
            self.image = pygame.transform.smoothscale(self.image, (70, 45))
        elif self.kind == "oil":
            self.image = pygame.transform.smoothscale(self.image, (55, 35))
        else:
            self.image = pygame.transform.smoothscale(self.image, (55, 40))

    def reset_position(self, player_rect):
        self.kind = random.choice(["barrier", "oil", "pothole"])
        self.load_image()

        self.rect = self.image.get_rect()
        self.rect.center = (safe_x(player_rect), random.randint(-900, -150))

    def move(self, player_rect):
        self.rect.move_ip(0, ENEMY_SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position(player_rect)


class RoadEvent(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.kind = random.choice(["moving_barrier", "speed_bump", "nitro_strip"])
        self.image = None
        self.rect = None
        self.direction = random.choice([-2, 2])
        self.reset_position(player_rect)

    def load_image(self):
        self.image = pygame.image.load(SPRITES[self.kind]).convert_alpha()

        if self.kind == "moving_barrier":
            self.image = pygame.transform.smoothscale(self.image, (90, 45))
        elif self.kind == "speed_bump":
            self.image = pygame.transform.smoothscale(self.image, (100, 35))
        else:
            self.image = pygame.transform.smoothscale(self.image, (100, 35))

    def reset_position(self, player_rect):
        self.kind = random.choice(["moving_barrier", "speed_bump", "nitro_strip"])
        self.load_image()

        self.rect = self.image.get_rect()
        self.rect.center = (safe_x(player_rect), random.randint(-1300, -500))
        self.direction = random.choice([-2, 2])

    def move(self, player_rect):
        self.rect.move_ip(self.direction, ENEMY_SPEED)

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1

        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position(player_rect)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.kind = random.choice(["nitro", "shield", "repair"])
        self.spawn_time = time.time()
        self.timeout = 7
        self.image = None
        self.rect = None
        self.reset_position(player_rect)

    def load_image(self):
        self.image = pygame.image.load(SPRITES[self.kind]).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (45, 45))

    def reset_position(self, player_rect):
        self.kind = random.choice(["nitro", "shield", "repair"])
        self.load_image()

        self.rect = self.image.get_rect()
        self.rect.center = (safe_x(player_rect), random.randint(-1200, -250))
        self.spawn_time = time.time()

    def move(self, player_rect):
        self.rect.move_ip(0, COIN_SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position(player_rect)

        if time.time() - self.spawn_time > self.timeout:
            self.reset_position(player_rect)


def ask_username():
    username = ""

    while True:
        DISPLAYSURF.fill((40, 40, 40))

        draw_text("Enter name", font_medium, WHITE, 105, 170)
        draw_text(username + "|", font_medium, WHITE, 80, 240)
        draw_text("Press Enter", font_small, WHITE, 125, 310)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if username == "":
                        username = "Player"
                    return username

                elif event.key == K_BACKSPACE:
                    username = username[:-1]

                elif len(username) < 12:
                    username += event.unicode

        pygame.display.update()
        FramePerSec.tick(FPS)


def game_loop(settings, username):
    global SCORE, COIN_COUNT, ENEMY_SPEED, COIN_SPEED, next_speedup
    global DISTANCE, POWER_BONUS

    SCORE = 0
    COIN_COUNT = 0
    DISTANCE = 0
    POWER_BONUS = 0

    next_speedup = COINS_FOR_SPEEDUP

    if settings["difficulty"] == "easy":
        ENEMY_SPEED = 4
        COIN_SPEED = 4
        finish_distance = 1500
    elif settings["difficulty"] == "hard":
        ENEMY_SPEED = 6
        COIN_SPEED = 6
        finish_distance = 2500
    else:
        ENEMY_SPEED = 5
        COIN_SPEED = 5
        finish_distance = 2000

    P1 = Player(settings)
    E1 = Enemy(P1.rect)
    C1 = Coin(P1.rect)
    O1 = Obstacle(P1.rect)
    R1 = RoadEvent(P1.rect)
    PU1 = PowerUp(P1.rect)

    enemies = pygame.sprite.Group()
    enemies.add(E1)

    coins = pygame.sprite.Group()
    coins.add(C1)

    obstacles = pygame.sprite.Group()
    obstacles.add(O1)

    road_events = pygame.sprite.Group()
    road_events.add(R1)

    powerups = pygame.sprite.Group()
    powerups.add(PU1)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(P1)
    all_sprites.add(E1)
    all_sprites.add(C1)
    all_sprites.add(O1)
    all_sprites.add(R1)
    all_sprites.add(PU1)

    INC_SPEED = pygame.USEREVENT + 1
    pygame.time.set_timer(INC_SPEED, 1000)

    active_power = None
    active_power_end = 0
    shield_active = False
    slow_end = 0

    saved_result = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == INC_SPEED:
                COIN_SPEED += 0.1

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "menu"

        if active_power == "nitro":
            if time.time() > active_power_end:
                active_power = None
            else:
                ENEMY_SPEED += 0.03
                COIN_SPEED += 0.03

        if time.time() < slow_end:
            P1.speed = 3
        else:
            P1.speed = PLAYER_SPEED

        difficulty_level = int(DISTANCE / 500)

        if len(enemies) < 1 + difficulty_level:
            new_enemy = Enemy(P1.rect)
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        if len(obstacles) < 1 + difficulty_level:
            new_obstacle = Obstacle(P1.rect)
            obstacles.add(new_obstacle)
            all_sprites.add(new_obstacle)

        DISPLAYSURF.blit(background, (0, 0))

        scores = font_small.render("Score: " + str(calculate_score()), True, BLACK)
        DISPLAYSURF.blit(scores, (10, 10))

        coin_text = font_small.render("Coins: " + str(COIN_COUNT), True, BLACK)
        DISPLAYSURF.blit(coin_text, (SCREEN_WIDTH - 120, 10))

        speed_text = font_small.render("Enemy speed: " + str(round(ENEMY_SPEED, 1)), True, BLACK)
        DISPLAYSURF.blit(speed_text, (10, 35))

        distance_text = font_small.render("Distance: " + str(int(DISTANCE)), True, BLACK)
        DISPLAYSURF.blit(distance_text, (10, 60))

        left_text = font_small.render("Left: " + str(int(finish_distance - DISTANCE)), True, BLACK)
        DISPLAYSURF.blit(left_text, (10, 85))

        if active_power == "nitro":
            left = int(active_power_end - time.time())
            power_text = font_small.render("Power: Nitro " + str(left), True, BLACK)
        elif active_power == "shield":
            power_text = font_small.render("Power: Shield", True, BLACK)
        else:
            power_text = font_small.render("Power: None", True, BLACK)

        DISPLAYSURF.blit(power_text, (10, 110))

        for entity in all_sprites:
            DISPLAYSURF.blit(entity.image, entity.rect)

            if isinstance(entity, Player):
                entity.move()
            else:
                entity.move(P1.rect)

        coin_hit = pygame.sprite.spritecollideany(P1, coins)

        if coin_hit:
            COIN_COUNT += coin_hit.weight
            coin_hit.reset_position(P1.rect)

            if COIN_COUNT >= next_speedup:
                ENEMY_SPEED += 1
                next_speedup += COINS_FOR_SPEEDUP

        power_hit = pygame.sprite.spritecollideany(P1, powerups)

        if power_hit:
            if active_power is None:
                if power_hit.kind == "nitro":
                    active_power = "nitro"
                    active_power_end = time.time() + 4
                    POWER_BONUS += 30

                elif power_hit.kind == "shield":
                    active_power = "shield"
                    shield_active = True
                    POWER_BONUS += 20

                elif power_hit.kind == "repair":
                    if len(obstacles) > 0:
                        first_obstacle = list(obstacles)[0]
                        first_obstacle.reset_position(P1.rect)
                    POWER_BONUS += 15

            power_hit.reset_position(P1.rect)

        obstacle_hit = pygame.sprite.spritecollideany(P1, obstacles)

        if obstacle_hit:
            if obstacle_hit.kind == "oil":
                slow_end = time.time() + 2
                obstacle_hit.reset_position(P1.rect)

            elif obstacle_hit.kind == "barrier" or obstacle_hit.kind == "pothole":
                if shield_active:
                    shield_active = False
                    active_power = None
                    obstacle_hit.reset_position(P1.rect)

                    if settings["sound"]:
                        crash_sound.play()
                else:
                    if settings["sound"]:
                        crash_sound.play()

                    time.sleep(0.5)

                    if not saved_result:
                        add_score_to_leaderboard(username, calculate_score(), DISTANCE, COIN_COUNT)
                        saved_result = True

                    return game_over_screen(calculate_score(), DISTANCE, COIN_COUNT)

        road_event_hit = pygame.sprite.spritecollideany(P1, road_events)

        if road_event_hit:
            if road_event_hit.kind == "moving_barrier":
                if shield_active:
                    shield_active = False
                    active_power = None
                    road_event_hit.reset_position(P1.rect)

                    if settings["sound"]:
                        crash_sound.play()
                else:
                    if settings["sound"]:
                        crash_sound.play()

                    time.sleep(0.5)

                    if not saved_result:
                        add_score_to_leaderboard(username, calculate_score(), DISTANCE, COIN_COUNT)
                        saved_result = True

                    return game_over_screen(calculate_score(), DISTANCE, COIN_COUNT)

            elif road_event_hit.kind == "speed_bump":
                slow_end = time.time() + 2
                road_event_hit.reset_position(P1.rect)

            elif road_event_hit.kind == "nitro_strip":
                if active_power is None:
                    active_power = "nitro"
                    active_power_end = time.time() + 3
                    POWER_BONUS += 10

                road_event_hit.reset_position(P1.rect)

        enemy_hit = pygame.sprite.spritecollideany(P1, enemies)

        if enemy_hit:
            if shield_active:
                shield_active = False
                active_power = None
                enemy_hit.reset_position(P1.rect)

                if settings["sound"]:
                    crash_sound.play()
            else:
                if settings["sound"]:
                    crash_sound.play()

                time.sleep(0.5)

                if not saved_result:
                    add_score_to_leaderboard(username, calculate_score(), DISTANCE, COIN_COUNT)
                    saved_result = True

                return game_over_screen(calculate_score(), DISTANCE, COIN_COUNT)

        DISTANCE += ENEMY_SPEED * 0.05

        if DISTANCE >= finish_distance:
            if not saved_result:
                add_score_to_leaderboard(username, calculate_score(), DISTANCE, COIN_COUNT)
                saved_result = True

            return game_over_screen(calculate_score(), DISTANCE, COIN_COUNT)

        pygame.display.update()
        FramePerSec.tick(FPS)


def game_over_screen(score, distance, coins):
    retry_button = pygame.Rect(110, 340, 180, 50)
    menu_button = pygame.Rect(110, 410, 180, 50)

    while True:
        DISPLAYSURF.fill(RED)

        DISPLAYSURF.blit(game_over_text, (30, 120))

        draw_text("Score: " + str(score), font_small, BLACK, 115, 220)
        draw_text("Distance: " + str(int(distance)), font_small, BLACK, 115, 250)
        draw_text("Coins: " + str(coins), font_small, BLACK, 115, 280)

        draw_button(retry_button, "Retry")
        draw_button(menu_button, "Main Menu")

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):
                    return "retry"

                if menu_button.collidepoint(event.pos):
                    return "menu"

        pygame.display.update()
        FramePerSec.tick(FPS)


def leaderboard_screen():
    back_button = pygame.Rect(110, 520, 180, 50)

    while True:
        DISPLAYSURF.fill((40, 40, 40))

        draw_text("Leaderboard", font_medium, WHITE, 90, 40)

        data = load_leaderboard()

        y = 100
        rank = 1

        for item in data[:10]:
            line = str(rank) + ". " + item["name"] + " | " + str(item["score"]) + " | " + str(item["distance"])
            draw_text(line, font_tiny, WHITE, 35, y)
            y += 35
            rank += 1

        draw_button(back_button, "Back")

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return

        pygame.display.update()
        FramePerSec.tick(FPS)


def settings_screen(settings):
    sound_button = pygame.Rect(80, 140, 240, 45)
    color_button = pygame.Rect(80, 210, 240, 45)
    difficulty_button = pygame.Rect(80, 280, 240, 45)
    back_button = pygame.Rect(80, 420, 240, 45)

    colors = ["default", "red", "blue", "green"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        DISPLAYSURF.fill((40, 40, 40))

        draw_text("Settings", font_medium, WHITE, 125, 60)

        draw_button(sound_button, "Sound: " + str(settings["sound"]))
        draw_button(color_button, "Car: " + settings["car_color"])
        draw_button(difficulty_button, "Difficulty: " + settings["difficulty"])
        draw_button(back_button, "Back")

        for event in pygame.event.get():
            if event.type == QUIT:
                save_settings(settings)
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                if sound_button.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                    save_settings(settings)

                elif color_button.collidepoint(event.pos):
                    index = colors.index(settings["car_color"])
                    settings["car_color"] = colors[(index + 1) % len(colors)]
                    save_settings(settings)

                elif difficulty_button.collidepoint(event.pos):
                    index = difficulties.index(settings["difficulty"])
                    settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]
                    save_settings(settings)

                elif back_button.collidepoint(event.pos):
                    save_settings(settings)
                    return

        pygame.display.update()
        FramePerSec.tick(FPS)


def main_menu():
    settings = load_settings()

    play_button = pygame.Rect(110, 180, 180, 50)
    leaderboard_button = pygame.Rect(110, 250, 180, 50)
    settings_button = pygame.Rect(110, 320, 180, 50)
    quit_button = pygame.Rect(110, 390, 180, 50)

    while True:
        DISPLAYSURF.fill((40, 130, 40))

        draw_text("RACER", font, WHITE, 95, 70)

        draw_button(play_button, "Play")
        draw_button(leaderboard_button, "Leaderboard")
        draw_button(settings_button, "Settings")
        draw_button(quit_button, "Quit")

        for event in pygame.event.get():
            if event.type == QUIT:
                save_settings(settings)
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    username = ask_username()
                    result = game_loop(settings, username)

                    while result == "retry":
                        username = ask_username()
                        result = game_loop(settings, username)

                    settings = load_settings()

                elif leaderboard_button.collidepoint(event.pos):
                    leaderboard_screen()

                elif settings_button.collidepoint(event.pos):
                    settings_screen(settings)
                    settings = load_settings()

                elif quit_button.collidepoint(event.pos):
                    save_settings(settings)
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        FramePerSec.tick(FPS)


main_menu()