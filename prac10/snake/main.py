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
RED = (255, 0, 0)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 20)

# Walls: simple border walls
# Snake is allowed only inside the inner area
PLAY_MIN_X = 1
PLAY_MAX_X = GRID_WIDTH - 2
PLAY_MIN_Y = 1
PLAY_MAX_Y = GRID_HEIGHT - 2


# -------------------- Functions --------------------
def draw_grid():
    # Draw border walls
    for x in range(GRID_WIDTH):
        pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, (GRID_HEIGHT - 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for y in range(GRID_HEIGHT):
        pygame.draw.rect(screen, GRAY, (0, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, ((GRID_WIDTH - 1) * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, GREEN,
                         (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_food(food):
    pygame.draw.rect(screen, RED, (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def random_food_position(snake):
    # Generate food only inside playable area and not on snake body
    while True:
        x = random.randint(PLAY_MIN_X, PLAY_MAX_X)
        y = random.randint(PLAY_MIN_Y, PLAY_MAX_Y)
        if [x, y] not in snake:
            return [x, y]


def show_text(score, level):
    score_text = font.render("Score: " + str(score), True, WHITE)
    level_text = font.render("Level: " + str(level), True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (120, 10))


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

score = 0
level = 1
speed = 7  # initial FPS

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

    # Current head
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

    # Check border collision (wall collision / leaving area)
    if head_x < PLAY_MIN_X or head_x > PLAY_MAX_X or head_y < PLAY_MIN_Y or head_y > PLAY_MAX_Y:
        game_over()

    # Check collision with itself
    if new_head in snake:
        game_over()

    snake.insert(0, new_head)

    # Check food collision
    if new_head == food:
        score += 1

        # Level up every 4 foods
        if score % 4 == 0:
            level += 1
            speed += 2

        food = random_food_position(snake)
    else:
        snake.pop()

    # Draw everything
    screen.fill(BLACK)
    draw_grid()
    draw_snake(snake)
    draw_food(food)
    show_text(score, level)

    pygame.display.update()
    clock.tick(speed)