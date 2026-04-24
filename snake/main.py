import pygame
import sys
import random

pygame.init()

# -------------------- Constants --------------------
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
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake - Practice 11")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 20)

# Walls are drawn around the field
PLAY_MIN_X = 1
PLAY_MAX_X = GRID_WIDTH - 2
PLAY_MIN_Y = 1
PLAY_MAX_Y = GRID_HEIGHT - 2

# Food disappears after this many milliseconds
FOOD_LIFETIME = 5000


def draw_grid():
    # Draw top and bottom walls
    for x in range(GRID_WIDTH):
        pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, (GRID_HEIGHT - 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw left and right walls
    for y in range(GRID_HEIGHT):
        pygame.draw.rect(screen, GRAY, (0, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, ((GRID_WIDTH - 1) * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, GREEN,
                         (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_food(food, weight):
    # Different food weights have different colors
    if weight == 1:
        color = RED
    elif weight == 2:
        color = ORANGE
    else:
        color = YELLOW

    pygame.draw.rect(screen, color,
                     (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def random_food_position(snake):
    # Generate food so it does not appear on snake or on wall
    while True:
        x = random.randint(PLAY_MIN_X, PLAY_MAX_X)
        y = random.randint(PLAY_MIN_Y, PLAY_MAX_Y)
        if [x, y] not in snake:
            return [x, y]


def show_text(score, food_weight, seconds_left):
    score_text = font.render("Score: " + str(score), True, WHITE)
    weight_text = font.render("Food weight: " + str(food_weight), True, WHITE)
    timer_text = font.render("Timer: " + str(seconds_left), True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(weight_text, (140, 10))
    screen.blit(timer_text, (320, 10))


def game_over():
    over_font = pygame.font.SysFont("Verdana", 40)
    text = over_font.render("Game Over", True, WHITE)
    screen.fill(BLACK)
    screen.blit(text, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 20))
    pygame.display.update()
    pygame.time.delay(2000)
    pygame.quit()
    sys.exit()


# -------------------- Initial game state --------------------
snake = [[10, 10], [9, 10], [8, 10]]
direction = "RIGHT"
next_direction = "RIGHT"

food = random_food_position(snake)
food_weight = random.randint(1, 3)
food_spawn_time = pygame.time.get_ticks()

score = 0
speed = 7

# -------------------- Main loop --------------------
while True:
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

    direction = next_direction

    # Current head position
    head_x = snake[0][0]
    head_y = snake[0][1]

    # Move snake
    if direction == "UP":
        head_y -= 1
    elif direction == "DOWN":
        head_y += 1
    elif direction == "LEFT":
        head_x -= 1
    elif direction == "RIGHT":
        head_x += 1

    new_head = [head_x, head_y]

    # Check wall collision
    if head_x < PLAY_MIN_X or head_x > PLAY_MAX_X or head_y < PLAY_MIN_Y or head_y > PLAY_MAX_Y:
        game_over()

    # Check collision with itself
    if new_head in snake:
        game_over()

    # Add new head
    snake.insert(0, new_head)

    # Check if snake eats food
    if new_head == food:
        score += food_weight

        # New food appears with new random weight and timer
        food = random_food_position(snake)
        food_weight = random.randint(1, 3)
        food_spawn_time = pygame.time.get_ticks()
    else:
        snake.pop()

    # Check if food should disappear
    current_time = pygame.time.get_ticks()
    if current_time - food_spawn_time > FOOD_LIFETIME:
        food = random_food_position(snake)
        food_weight = random.randint(1, 3)
        food_spawn_time = current_time

    seconds_left = max(0, (FOOD_LIFETIME - (current_time - food_spawn_time)) // 1000)

    # Draw everything
    screen.fill(BLACK)
    draw_grid()
    draw_snake(snake)
    draw_food(food, food_weight)
    show_text(score, food_weight, seconds_left)

    pygame.display.update()
    clock.tick(speed)