import pygame, sys, random, time, json, os
from pygame.locals import *
from datetime import datetime

# init
pygame.init()
pygame.mixer.init()

FPS = 60
clock = pygame.time.Clock()

SCREEN_W, SCREEN_H = 400, 600
DISPLAYSURF = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Racer – TSIS 3")

RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
GREEN = (40, 130, 40)
DARK = (40, 40, 40)
GOLD = (255, 200, 0)

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def asset(filename):
    return os.path.join(ASSETS_DIR, filename)


#fonts
font_big = pygame.font.SysFont("Verdana", 60)
font_med = pygame.font.SysFont("Verdana", 30)
font_sm  = pygame.font.SysFont("Verdana", 20)
font_xs  = pygame.font.SysFont("Verdana", 15)
#other assets if norm ones are not loading
def load_img(path, size=None, fallback_color=(180, 50, 200)):
    try:
        img = pygame.image.load(path).convert_alpha()
    except Exception:
        surf = pygame.Surface(size or (40, 40), pygame.SRCALPHA)
        surf.fill((*fallback_color, 200))
        return surf
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img


BG_IMG = load_img(asset("AnimatedStreet.png"), (SCREEN_W, SCREEN_H))

try:
    crash_sound = pygame.mixer.Sound(asset("crash.wav"))
except Exception:
    crash_sound = None

# pre-load every sprite once so classes never hit the disk again
IMGS = {
    "player": load_img(asset("Player.png")),
    "enemy": load_img(asset("Enemy.png")),
    "coin1": load_img(asset("Coin.png"), (40, 40)),
    "coin2": load_img(asset("Coins.png"), (40, 40)),
    "coin3": load_img(asset("MoreCoins.png"), (40, 40)),
    "barrier": load_img(asset("Barrier.png"), (70, 45)),
    "oil": load_img(asset("Oil.png"), (55, 35)),
    "pothole": load_img(asset("Pothole.png"), (55, 40)),
    "moving_barrier": load_img(asset("MovingBarrier.png"), (90, 45)),
    "speed_bump": load_img(asset("SpeedBump.png"), (100, 35)),
    "nitro_strip": load_img(asset("NitroStrip.png"), (100, 35)),
    "nitro": load_img(asset("Nitro.png"), (45, 45)),
    "shield": load_img(asset("Shield.png"), (45, 45)),
    "repair": load_img(asset("Repair.png"), (45, 45)),
}



#  constants

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    return {"sound": True, "car_color": "default", "difficulty": "normal"}


def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=4)


def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    return []


def save_leaderboard(data):
    data = sorted(data, key=lambda x: x["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_to_leaderboard(name, score, distance, coins):
    data = load_leaderboard()
    data.append({
        "name": name,
        "score": score,
        "distance": int(distance),
        "coins": coins,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_leaderboard(data)


def draw_text(text, font, color, x, y):
    DISPLAYSURF.blit(font.render(text, True, color), (x, y))


def draw_button(rect, label):
    pygame.draw.rect(DISPLAYSURF, WHITE, rect)
    pygame.draw.rect(DISPLAYSURF, BLACK, rect, 2)
    surf = font_sm.render(label, True, BLACK)
    DISPLAYSURF.blit(surf, (rect.x + 14, rect.y + 12))


def tint_image(img, color_name):
    tints = {"red": (200, 0, 0), "blue": (0, 0, 200), "green": (0, 180, 0)}
    if color_name not in tints:
        return img
    tinted = img.copy()
    overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    overlay.fill((*tints[color_name], 80))
    tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted


def safe_x(player_cx, margin=45):
    for _ in range(60):
        x = random.randint(40, SCREEN_W - 40)
        if abs(x - player_cx) > margin:
            return x
    return random.randint(40, SCREEN_W - 40)


def calc_score(coins, distance, power_bonus):
    return coins * 10 + int(distance / 5) + power_bonus


def play_sound(enabled):
    if enabled and crash_sound:
        crash_sound.play()



#sprites
class Player(pygame.sprite.Sprite):
    BASE_SPEED = 5

    def __init__(self, car_color):
        super().__init__()
        self.image = tint_image(IMGS["player"].copy(), car_color)
        self.rect = self.image.get_rect(center=(160, 520))
        self.speed = self.BASE_SPEED

    def move(self):
        keys = pygame.key.get_pressed()
        if self.rect.left > 0 and keys[K_LEFT]:  self.rect.x -= self.speed
        if self.rect.right < SCREEN_W and keys[K_RIGHT]: self.rect.x += self.speed


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_cx):
        super().__init__()
        self.image = IMGS["enemy"].copy()
        self.rect = self.image.get_rect()
        self._place(player_cx)

    def _place(self, player_cx):
        self.rect.center = (safe_x(player_cx), random.randint(-700, -80))

    def update(self, player_cx, speed):
        self.rect.y += speed
        if self.rect.top > SCREEN_H:
            self._place(player_cx)


class Coin(pygame.sprite.Sprite):
    _IMG_KEY = {1: "coin1", 2: "coin2", 3: "coin3"}

    def __init__(self, player_cx):
        super().__init__()
        self.weight = 1
        self.image = IMGS["coin1"]
        self.rect = self.image.get_rect()
        self._place(player_cx)

    def _place(self, player_cx):
        self.weight = random.randint(1, 3)
        self.image = IMGS[self._IMG_KEY[self.weight]]
        self.rect = self.image.get_rect(
            center=(safe_x(player_cx), random.randint(-600, -50))
        )

    def update(self, player_cx, speed):
        self.rect.y += speed
        if self.rect.top > SCREEN_H:
            self._place(player_cx)


class Obstacle(pygame.sprite.Sprite):
    KINDS = ["barrier", "oil", "pothole"]

    def __init__(self, player_cx):
        super().__init__()
        self.kind = "barrier"
        self.image = IMGS["barrier"]
        self.rect = self.image.get_rect()
        self._place(player_cx)

    def _place(self, player_cx):
        self.kind = random.choice(self.KINDS)
        self.image = IMGS[self.kind]
        self.rect = self.image.get_rect(
            center=(safe_x(player_cx), random.randint(-900, -150))
        )

    def update(self, player_cx, speed):
        self.rect.y += speed
        if self.rect.top > SCREEN_H:
            self._place(player_cx)


class RoadEvent(pygame.sprite.Sprite):
    KINDS = ["moving_barrier", "speed_bump", "nitro_strip"]

    def __init__(self, player_cx):
        super().__init__()
        self.kind = "speed_bump"
        self.image = IMGS["speed_bump"]
        self.rect = self.image.get_rect()
        self.dx = 2
        self._place(player_cx)

    def _place(self, player_cx):
        self.kind = random.choice(self.KINDS)
        self.image = IMGS[self.kind]
        self.rect = self.image.get_rect(
            center=(safe_x(player_cx), random.randint(-1300, -500))
        )
        self.dx = random.choice([-2, 2])

    def update(self, player_cx, speed):
        self.rect.x += self.dx
        self.rect.y += speed
        if self.rect.left < 0 or self.rect.right > SCREEN_W:
            self.dx *= -1
        if self.rect.top > SCREEN_H:
            self._place(player_cx)


class PowerUp(pygame.sprite.Sprite):
    KINDS = ["nitro", "shield", "repair"]
    TIMEOUT = 5

    def __init__(self, player_cx):
        super().__init__()
        self.kind = "nitro"
        self.image = IMGS["nitro"]
        self.rect = self.image.get_rect()
        self.spawn_time = time.time()
        self._place(player_cx)

    def _place(self, player_cx):
        self.kind = random.choice(self.KINDS)
        self.image = IMGS[self.kind]
        self.rect = self.image.get_rect(
            center=(safe_x(player_cx), random.randint(-1200, -250))
        )
        self.spawn_time = time.time()

    def update(self, player_cx, speed):
        self.rect.y += speed
        if self.rect.top > SCREEN_H or time.time() - self.spawn_time > self.TIMEOUT:
            self._place(player_cx)


#screens
def ask_username():
    name = ""
    while True:
        DISPLAYSURF.fill(DARK)
        draw_text("Enter your name", font_med, WHITE, 70, 170)
        draw_text(name + "|", font_med, WHITE, 80, 240)
        draw_text("Press Enter to start", font_sm, GRAY, 85, 310)
        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit();
                sys.exit()
            if ev.type == KEYDOWN:
                if ev.key == K_RETURN:
                    return name.strip() or "Player"
                elif ev.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 12:
                    name += ev.unicode
        clock.tick(FPS)


def game_over_screen(score, distance, coins):
    retry_btn = pygame.Rect(110, 350, 180, 50)
    menu_btn = pygame.Rect(110, 420, 180, 50)

    while True:
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(font_big.render("Game Over", True, BLACK), (25, 110))
        draw_text(f"Score:    {score}", font_sm, BLACK, 115, 220)
        draw_text(f"Distance: {int(distance)}", font_sm, BLACK, 115, 250)
        draw_text(f"Coins:    {coins}", font_sm, BLACK, 115, 280)
        draw_button(retry_btn, "Retry")
        draw_button(menu_btn, "Main Menu")
        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit();
                sys.exit()
            if ev.type == MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(ev.pos): return "retry"
                if menu_btn.collidepoint(ev.pos):  return "menu"
        clock.tick(FPS)


def leaderboard_screen():
    back_btn = pygame.Rect(110, 530, 180, 45)

    while True:
        DISPLAYSURF.fill(DARK)
        draw_text("Leaderboard", font_med, WHITE, 90, 25)
        draw_text(f"{'#':<3} {'Name':<13} {'Score':<8} Dist", font_xs, GRAY, 28, 72)

        for i, item in enumerate(load_leaderboard()):
            row = f"{i + 1:<3} {item['name']:<13} {item['score']:<8} {item['distance']}"
            draw_text(row, font_xs, WHITE, 28, 97 + i * 38)

        draw_button(back_btn, "Back")
        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit();
                sys.exit()
            if ev.type == MOUSEBUTTONDOWN:
                if back_btn.collidepoint(ev.pos): return
        clock.tick(FPS)


def settings_screen(settings):
    btns = {
        "sound": pygame.Rect(80, 140, 240, 45),
        "car_color": pygame.Rect(80, 210, 240, 45),
        "difficulty": pygame.Rect(80, 280, 240, 45),
        "back": pygame.Rect(80, 420, 240, 45),
    }
    colors = ["default", "red", "blue", "green"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        DISPLAYSURF.fill(DARK)
        draw_text("Settings", font_med, WHITE, 130, 60)
        draw_button(btns["sound"], f"Sound: {'On' if settings['sound'] else 'Off'}")
        draw_button(btns["car_color"], f"Car color: {settings['car_color']}")
        draw_button(btns["difficulty"], f"Difficulty: {settings['difficulty']}")
        draw_button(btns["back"], "Back")
        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == QUIT:
                save_settings(settings);
                pygame.quit();
                sys.exit()
            if ev.type == MOUSEBUTTONDOWN:
                if btns["sound"].collidepoint(ev.pos):
                    settings["sound"] = not settings["sound"]
                elif btns["car_color"].collidepoint(ev.pos):
                    i = colors.index(settings["car_color"])
                    settings["car_color"] = colors[(i + 1) % len(colors)]
                elif btns["difficulty"].collidepoint(ev.pos):
                    i = difficulties.index(settings["difficulty"])
                    settings["difficulty"] = difficulties[(i + 1) % len(difficulties)]
                elif btns["back"].collidepoint(ev.pos):
                    save_settings(settings);
                    return
        clock.tick(FPS)


#game loop
def game_loop(settings, username):
    # ── Per-difficulty setup ──────────────────────────
    diff = settings["difficulty"]
    base_enemy_speed = {"easy": 4, "normal": 5, "hard": 6}[diff]
    coin_speed = float(base_enemy_speed)
    enemy_speed = float(base_enemy_speed)
    finish_dist = {"easy": 1500, "normal": 2000, "hard": 2500}[diff]

    coins_collected = 0
    distance = 0
    power_bonus = 0
    next_speedup = 5  # collect this many coins to bump enemy speed

    # Power-up state
    active_power = None  # "nitro" | "shield" | None
    power_end = 0.0  # epoch when nitro expires
    slow_until = 0.0  # epoch when slow effect expires

    # ── Sprite setup ─────────────────────────────────
    player = Player(settings["car_color"])
    pcx = player.rect.centerx  # player center-x, updated each frame

    enemies = pygame.sprite.Group(Enemy(pcx))
    coins = pygame.sprite.Group(Coin(pcx), Coin(pcx), Coin(pcx))
    obstacles = pygame.sprite.Group(Obstacle(pcx))
    road_evts = pygame.sprite.Group(RoadEvent(pcx))
    powerups = pygame.sprite.Group(PowerUp(pcx))

    all_sprites = pygame.sprite.Group(
        player, *enemies, *coins, *obstacles, *road_evts, *powerups
    )

    saved = False  # guard: only write leaderboard entry once

    def finish_run():
        nonlocal saved
        final = calc_score(coins_collected, distance, power_bonus)
        if not saved:
            add_to_leaderboard(username, final, distance, coins_collected)
            saved = True
        return game_over_screen(final, distance, coins_collected)

    def absorb_with_shield(sprite):
        """Shield blocks one hit, then deactivates."""
        nonlocal active_power
        sprite._place(pcx)
        active_power = None
        play_sound(settings["sound"])

    #Main loop
    while True:
        # Events
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit();
                sys.exit()
            if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                return "menu"

        pcx = player.rect.centerx

        # ── Effective speed this frame ────────────────
        if active_power == "nitro":
            if time.time() > power_end:
                active_power = None
                eff_speed = enemy_speed
            else:
                eff_speed = enemy_speed * 1.5
        else:
            eff_speed = enemy_speed

        player.speed = 3 if time.time() < slow_until else Player.BASE_SPEED

        # ── Difficulty scaling: add sprites as distance grows ──
        level = int(distance / 500)
        while len(enemies) < 1 + level:
            e = Enemy(pcx);
            enemies.add(e);
            all_sprites.add(e)
        while len(obstacles) < 1 + level:
            o = Obstacle(pcx);
            obstacles.add(o);
            all_sprites.add(o)

        player.move()
        for s in enemies:   s.update(pcx, eff_speed)
        for s in coins:     s.update(pcx, coin_speed)
        for s in obstacles: s.update(pcx, eff_speed)
        for s in road_evts: s.update(pcx, eff_speed)
        for s in powerups:  s.update(pcx, coin_speed)

        coin_hit = pygame.sprite.spritecollideany(player, coins)
        if coin_hit:
            coins_collected += coin_hit.weight
            coin_hit._place(pcx)
            if coins_collected >= next_speedup:
                enemy_speed += 1
                next_speedup += 5

        pu_hit = pygame.sprite.spritecollideany(player, powerups)
        if pu_hit and active_power is None:
            if pu_hit.kind == "nitro":
                active_power = "nitro"
                power_end = time.time() + 4
                power_bonus += 30
            elif pu_hit.kind == "shield":
                active_power = "shield"
                power_bonus += 20
            elif pu_hit.kind == "repair":
                # clear the nearest obstacle so the player survives
                nearest = min(
                    obstacles,
                    key=lambda o: abs(o.rect.centery - player.rect.centery),
                    default=None
                )
                if nearest:
                    nearest._place(pcx)
                power_bonus += 15
            pu_hit._place(pcx)
        obs_hit = pygame.sprite.spritecollideany(player, obstacles)
        if obs_hit:
            if obs_hit.kind == "oil":
                slow_until = time.time() + 2
                obs_hit._place(pcx)
            elif active_power == "shield":
                absorb_with_shield(obs_hit)
            else:
                play_sound(settings["sound"])
                time.sleep(0.5)
                return finish_run()

        rev_hit = pygame.sprite.spritecollideany(player, road_evts)
        if rev_hit:
            if rev_hit.kind == "speed_bump":
                slow_until = time.time() + 2
                rev_hit._place(pcx)
            elif rev_hit.kind == "nitro_strip":
                if active_power is None:
                    active_power = "nitro"
                    power_end = time.time() + 3
                    power_bonus += 10
                rev_hit._place(pcx)
            elif rev_hit.kind == "moving_barrier":
                if active_power == "shield":
                    absorb_with_shield(rev_hit)
                else:
                    play_sound(settings["sound"])
                    time.sleep(0.5)
                    return finish_run()

        enemy_hit = pygame.sprite.spritecollideany(player, enemies)
        if enemy_hit:
            if active_power == "shield":
                absorb_with_shield(enemy_hit)
            else:
                play_sound(settings["sound"])
                time.sleep(0.5)
                return finish_run()

        distance += eff_speed * 0.05
        if distance >= finish_dist:
            return finish_run()

        DISPLAYSURF.blit(BG_IMG, (0, 0))

        for s in all_sprites:
            DISPLAYSURF.blit(s.image, s.rect)

        # HUD
        score_now = calc_score(coins_collected, distance, power_bonus)
        draw_text(f"Score: {score_now}", font_sm, BLACK, 10, 10)
        draw_text(f"Coins: {coins_collected}", font_sm, BLACK, SCREEN_W - 120, 10)
        draw_text(f"Speed: {eff_speed:.1f}", font_sm, BLACK, 10, 35)
        draw_text(f"Dist:  {int(distance)}", font_sm, BLACK, 10, 60)
        draw_text(f"Left:  {int(finish_dist - distance)}", font_sm, BLACK, 10, 85)

        if active_power == "nitro":
            draw_text(f"NITRO  {int(power_end - time.time())}s", font_sm, GOLD, 10, 110)
        elif active_power == "shield":
            draw_text("SHIELD active", font_sm, GOLD, 10, 110)

        pygame.display.update()
        clock.tick(FPS)

def main_menu():
    settings = load_settings()

    btns = {
        "play": pygame.Rect(110, 180, 180, 50),
        "leaderboard": pygame.Rect(110, 250, 180, 50),
        "settings": pygame.Rect(110, 320, 180, 50),
        "quit": pygame.Rect(110, 390, 180, 50),
    }
    labels = [("play", "Play"), ("leaderboard", "Leaderboard"),
              ("settings", "Settings"), ("quit", "Quit")]

    while True:
        DISPLAYSURF.fill(GREEN)
        DISPLAYSURF.blit(font_big.render("RACER", True, WHITE), (95, 70))
        for key, label in labels:
            draw_button(btns[key], label)
        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == QUIT:
                save_settings(settings);
                pygame.quit();
                sys.exit()

            if ev.type == MOUSEBUTTONDOWN:
                if btns["play"].collidepoint(ev.pos):
                    username = ask_username()
                    result = game_loop(settings, username)
                    while result == "retry":
                        username = ask_username()
                        result = game_loop(settings, username)
                    settings = load_settings()  # re-read in case settings changed mid-run

                elif btns["leaderboard"].collidepoint(ev.pos):
                    leaderboard_screen()

                elif btns["settings"].collidepoint(ev.pos):
                    settings_screen(settings)
                    settings = load_settings()

                elif btns["quit"].collidepoint(ev.pos):
                    save_settings(settings);
                    pygame.quit();
                    sys.exit()

        clock.tick(FPS)


main_menu()
