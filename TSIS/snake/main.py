import pygame
import sys
import random
import json
import os
import math
import array
from db import create_tables, save_result, get_top_scores, get_personal_best

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20

SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
DARK_RED = (120, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 120, 255)
PURPLE = (160, 0, 200)
CYAN = (0, 220, 220)

PLAY_MIN_X = 1
PLAY_MAX_X = GRID_WIDTH - 2
PLAY_MIN_Y = 1
PLAY_MAX_Y = GRID_HEIGHT - 2

FOOD_LIFETIME = 5000
POWER_LIFETIME = 8000
POWER_DURATION = 5000

SETTINGS_FILE = "settings.json"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake TSIS4")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Verdana", 20)
font_small = pygame.font.SysFont("Verdana", 16)
font_big = pygame.font.SysFont("Verdana", 38)


def make_sound():
    sample_rate = 44100
    duration = 0.08
    frequency = 700
    volume = 5000

    buf = array.array("h")

    for i in range(int(sample_rate * duration)):
        value = int(volume * math.sin(2 * math.pi * frequency * i / sample_rate))
        buf.append(value)

    return pygame.mixer.Sound(buffer=buf)


beep_sound = make_sound()


def play_sound(settings):
    if settings["sound"]:
        beep_sound.play()


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        f = open(SETTINGS_FILE, "r")
        data = json.load(f)
        f.close()
        return data

    return {
        "snake_color": [0, 200, 0],
        "grid": True,
        "sound": True
    }


def save_settings(settings):
    f = open(SETTINGS_FILE, "w")
    json.dump(settings, f, indent=4)
    f.close()


def draw_text(text, font_obj, color, x, y):
    img = font_obj.render(text, True, color)
    screen.blit(img, (x, y))


def draw_button(rect, text):
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    img = font_small.render(text, True, BLACK)
    screen.blit(img, (rect.x + 15, rect.y + 12))


def draw_walls():
    for x in range(GRID_WIDTH):
        pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, (GRID_HEIGHT - 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for y in range(GRID_HEIGHT):
        pygame.draw.rect(screen, GRAY, (0, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, ((GRID_WIDTH - 1) * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_grid_overlay():
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, SCREEN_HEIGHT))

    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (30, 30, 30), (0, y), (SCREEN_WIDTH, y))


def draw_snake(snake, settings):
    color = tuple(settings["snake_color"])

    for segment in snake:
        pygame.draw.rect(
            screen,
            color,
            (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )


def draw_food(food, weight):
    if weight == 1:
        color = RED
    elif weight == 2:
        color = ORANGE
    else:
        color = YELLOW

    pygame.draw.rect(
        screen,
        color,
        (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )


def draw_poison(poison):
    if poison is not None:
        pygame.draw.rect(
            screen,
            DARK_RED,
            (poison[0] * CELL_SIZE, poison[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )


def draw_powerup(powerup):
    if powerup is None:
        return

    kind = powerup["kind"]
    pos = powerup["pos"]

    if kind == "speed":
        color = BLUE
        letter = "B"
    elif kind == "slow":
        color = CYAN
        letter = "S"
    else:
        color = PURPLE
        letter = "H"

    pygame.draw.rect(
        screen,
        color,
        (pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )

    draw_text(letter, font_small, WHITE, pos[0] * CELL_SIZE + 4, pos[1] * CELL_SIZE)


def draw_obstacles(obstacles):
    for block in obstacles:
        pygame.draw.rect(
            screen,
            GRAY,
            (block[0] * CELL_SIZE, block[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )


def random_empty_position(snake, obstacles, extra):
    while True:
        x = random.randint(PLAY_MIN_X, PLAY_MAX_X)
        y = random.randint(PLAY_MIN_Y, PLAY_MAX_Y)
        pos = [x, y]

        if pos not in snake and pos not in obstacles and pos not in extra:
            return pos


def create_obstacles(level, snake, food, poison, powerup):
    if level < 3:
        return []

    obstacles = []
    count = level + 2

    head = snake[0]
    protected = [
        head,
        [head[0] + 1, head[1]],
        [head[0] - 1, head[1]],
        [head[0], head[1] + 1],
        [head[0], head[1] - 1],
        [head[0] + 2, head[1]],
        [head[0] - 2, head[1]],
        [head[0], head[1] + 2],
        [head[0], head[1] - 2]
    ]

    extra = []
    if food is not None:
        extra.append(food)
    if poison is not None:
        extra.append(poison)
    if powerup is not None:
        extra.append(powerup["pos"])

    while len(obstacles) < count:
        pos = random_empty_position(snake, obstacles, extra)

        if pos not in protected:
            obstacles.append(pos)

    return obstacles


def spawn_poison(snake, obstacles, food, powerup):
    extra = [food]

    if powerup is not None:
        extra.append(powerup["pos"])

    return random_empty_position(snake, obstacles, extra)


def spawn_powerup(snake, obstacles, food, poison):
    kinds = ["speed", "slow", "shield"]
    extra = [food]

    if poison is not None:
        extra.append(poison)

    return {
        "kind": random.choice(kinds),
        "pos": random_empty_position(snake, obstacles, extra),
        "spawn_time": pygame.time.get_ticks()
    }


def show_game_info(score, level, food_weight, seconds_left, username, best, active_power):
    draw_text("User: " + username, font_small, WHITE, 10, 5)
    draw_text("Best: " + str(best), font_small, WHITE, 130, 5)
    draw_text("Score: " + str(score), font_small, WHITE, 250, 5)
    draw_text("Level: " + str(level), font_small, WHITE, 360, 5)
    draw_text("Food: " + str(food_weight), font_small, WHITE, 455, 5)

    if active_power["kind"] is None:
        power_text = "Power: None"
    else:
        power_text = "Power: " + active_power["kind"]

    draw_text(power_text, font_small, WHITE, 10, 25)
    draw_text("Timer: " + str(seconds_left), font_small, WHITE, 160, 25)


def username_screen():
    username = ""

    while True:
        screen.fill(BLACK)

        draw_text("Enter username", font_big, WHITE, 140, 140)
        draw_text(username + "|", font_big, YELLOW, 170, 220)
        draw_text("Press Enter", font, WHITE, 220, 300)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username == "":
                        username = "Player"
                    return username

                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]

                elif len(username) < 12:
                    username += event.unicode

        pygame.display.update()
        clock.tick(60)


def game_loop(username, settings):
    personal_best = get_personal_best(username)

    snake = [[10, 10], [9, 10], [8, 10]]
    direction = "RIGHT"
    next_direction = "RIGHT"

    score = 0
    level = 1
    eaten_count = 0
    base_speed = 7

    obstacles = []

    food = random_empty_position(snake, obstacles, [])
    food_weight = random.randint(1, 3)
    food_spawn_time = pygame.time.get_ticks()

    poison = spawn_poison(snake, obstacles, food, None)

    powerup = None
    powerup_last_spawn = pygame.time.get_ticks()

    active_power = {
        "kind": None,
        "end_time": 0,
        "shield": False
    }

    while True:
        current_time = pygame.time.get_ticks()

        speed = base_speed + level - 1

        if active_power["kind"] == "speed":
            if current_time < active_power["end_time"]:
                speed += 4
            else:
                active_power["kind"] = None

        elif active_power["kind"] == "slow":
            if current_time < active_power["end_time"]:
                speed = max(4, speed - 3)
            else:
                active_power["kind"] = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != "DOWN":
                    next_direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    next_direction = "DOWN"
                elif event.key == pygame.K_LEFT and direction != "RIGHT":
                    next_direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    next_direction = "RIGHT"
                elif event.key == pygame.K_ESCAPE:
                    return "menu", score, level, personal_best

        direction = next_direction

        head_x = snake[0][0]
        head_y = snake[0][1]

        if direction == "UP":
            head_y -= 1
        elif direction == "DOWN":
            head_y += 1
        elif direction == "LEFT":
            head_x -= 1
        elif direction == "RIGHT":
            head_x += 1

        new_head = [head_x, head_y]

        wall_collision = head_x < PLAY_MIN_X or head_x > PLAY_MAX_X or head_y < PLAY_MIN_Y or head_y > PLAY_MAX_Y
        self_collision = new_head in snake
        obstacle_collision = new_head in obstacles

        if wall_collision or self_collision or obstacle_collision:
            if active_power["shield"]:
                active_power["shield"] = False
                active_power["kind"] = None
                new_head = snake[0][:]
            else:
                play_sound(settings)
                save_result(username, score, level)
                best_after = max(personal_best, score)
                return "game_over", score, level, best_after

        snake.insert(0, new_head)

        if new_head == food:
            score += food_weight
            eaten_count += 1
            play_sound(settings)

            i = 1
            while i < food_weight:
                snake.append(snake[-1][:])
                i +=1
            
            food = random_empty_position(snake, obstacles, [])
            food_weight = random.randint(1, 3)
            food_spawn_time = current_time

            if eaten_count % 3 == 0:
                level += 1
                obstacles = create_obstacles(level, snake, food, poison, powerup)

        elif poison is not None and new_head == poison:
            play_sound(settings)

            for i in range(2):
                if len(snake) > 0:
                    snake.pop()

            if len(snake) <= 1:
                save_result(username, score, level)
                best_after = max(personal_best, score)
                return "game_over", score, level, best_after

            poison = spawn_poison(snake, obstacles, food, powerup)

        elif powerup is not None and new_head == powerup["pos"]:
            play_sound(settings)

            if powerup["kind"] == "speed":
                active_power["kind"] = "speed"
                active_power["end_time"] = current_time + POWER_DURATION
                active_power["shield"] = False

            elif powerup["kind"] == "slow":
                active_power["kind"] = "slow"
                active_power["end_time"] = current_time + POWER_DURATION
                active_power["shield"] = False

            elif powerup["kind"] == "shield":
                active_power["kind"] = "shield"
                active_power["shield"] = True

            powerup = None
            powerup_last_spawn = current_time

        else:
            snake.pop()

        if current_time - food_spawn_time > FOOD_LIFETIME:
            food = random_empty_position(snake, obstacles, [])
            food_weight = random.randint(1, 3)
            food_spawn_time = current_time

        if poison is None or random.randint(1, 250) == 1:
            poison = spawn_poison(snake, obstacles, food, powerup)

        if powerup is None:
            if current_time - powerup_last_spawn > 6000:
                powerup = spawn_powerup(snake, obstacles, food, poison)

        else:
            if current_time - powerup["spawn_time"] > POWER_LIFETIME:
                powerup = None
                powerup_last_spawn = current_time

        food_seconds_left = max(0, (FOOD_LIFETIME - (current_time - food_spawn_time)) // 1000)

        screen.fill(BLACK)

        if settings["grid"]:
            draw_grid_overlay()

        draw_walls()
        draw_obstacles(obstacles)
        draw_snake(snake, settings)
        draw_food(food, food_weight)
        draw_poison(poison)
        draw_powerup(powerup)
        show_game_info(score, level, food_weight, food_seconds_left, username, personal_best, active_power)

        pygame.display.update()
        clock.tick(speed)


def game_over_screen(score, level, best):
    retry_button = pygame.Rect(200, 250, 200, 45)
    menu_button = pygame.Rect(200, 315, 200, 45)

    while True:
        screen.fill(BLACK)

        draw_text("Game Over", font_big, RED, 180, 100)
        draw_text("Score: " + str(score), font, WHITE, 220, 165)
        draw_text("Level: " + str(level), font, WHITE, 220, 195)
        draw_text("Personal best: " + str(best), font, WHITE, 180, 225)

        draw_button(retry_button, "Retry")
        draw_button(menu_button, "Main Menu")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):
                    return "retry"

                if menu_button.collidepoint(event.pos):
                    return "menu"

        pygame.display.update()
        clock.tick(60)


def leaderboard_screen():
    back_button = pygame.Rect(220, 350, 160, 40)

    while True:
        screen.fill(BLACK)

        draw_text("Leaderboard", font_big, WHITE, 170, 30)

        try:
            rows = get_top_scores()
        except:
            rows = []

        y = 95
        rank = 1

        draw_text("Rank  User       Score  Level  Date", font_small, YELLOW, 60, 70)

        for row in rows:
            username = row[0]
            score = row[1]
            level = row[2]
            date = str(row[3])[:16]

            line = str(rank) + ". " + username + "   " + str(score) + "   " + str(level) + "   " + date
            draw_text(line, font_small, WHITE, 60, y)

            y += 25
            rank += 1

        draw_button(back_button, "Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return

        pygame.display.update()
        clock.tick(60)


def settings_screen(settings):
    grid_button = pygame.Rect(190, 150, 220, 45)
    sound_button = pygame.Rect(190, 210, 220, 45)
    color_button = pygame.Rect(190, 270, 220, 45)
    back_button = pygame.Rect(190, 340, 220, 45)

    colors = [
        [0, 200, 0],
        [0, 120, 255],
        [255, 255, 0],
        [255, 0, 0],
        [160, 0, 200]
    ]

    while True:
        screen.fill(BLACK)

        draw_text("Settings", font_big, WHITE, 200, 70)

        draw_button(grid_button, "Grid: " + str(settings["grid"]))
        draw_button(sound_button, "Sound: " + str(settings["sound"]))
        draw_button(color_button, "Snake Color")
        draw_button(back_button, "Save & Back")

        pygame.draw.rect(screen, tuple(settings["snake_color"]), (430, 280, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_button.collidepoint(event.pos):
                    settings["grid"] = not settings["grid"]

                elif sound_button.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]

                elif color_button.collidepoint(event.pos):
                    current = settings["snake_color"]

                    index = 0
                    if current in colors:
                        index = colors.index(current)

                    settings["snake_color"] = colors[(index + 1) % len(colors)]

                elif back_button.collidepoint(event.pos):
                    save_settings(settings)
                    return

        pygame.display.update()
        clock.tick(60)


def main_menu():
    create_tables()

    settings = load_settings()
    username = username_screen()

    play_button = pygame.Rect(200, 160, 200, 45)
    leaderboard_button = pygame.Rect(200, 220, 200, 45)
    settings_button = pygame.Rect(200, 280, 200, 45)
    quit_button = pygame.Rect(200, 340, 200, 45)

    while True:
        screen.fill(BLACK)

        draw_text("Snake TSIS4", font_big, GREEN, 155, 60)
        draw_text("Player: " + username, font, WHITE, 210, 115)

        draw_button(play_button, "Play")
        draw_button(leaderboard_button, "Leaderboard")
        draw_button(settings_button, "Settings")
        draw_button(quit_button, "Quit")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    result, score, level, best = game_loop(username, settings)

                    if result == "game_over":
                        action = game_over_screen(score, level, best)

                        while action == "retry":
                            result, score, level, best = game_loop(username, settings)

                            if result == "game_over":
                                action = game_over_screen(score, level, best)
                            else:
                                action = "menu"

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
        clock.tick(60)


main_menu()