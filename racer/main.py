import pygame, sys
from pygame.locals import *
import random, time

# Initializing pygame
pygame.init()

# Setting up FPS
FPS = 60
FramePerSec = pygame.time.Clock()

# Creating colors
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Screen settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Game variables
PLAYER_SPEED = 5
ENEMY_SPEED = 5
COIN_SPEED = 5

SCORE = 0
COIN_COUNT = 0

# Every N collected coins enemy speed increases
COINS_FOR_SPEEDUP = 5
next_speedup = COINS_FOR_SPEEDUP

# Setting up fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Loading images and sounds
background = pygame.image.load("AnimatedStreet.png")
crash_sound = pygame.mixer.Sound("crash.wav")

# Creating game window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer - Practice 11")


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, ENEMY_SPEED)

        # If enemy leaves screen, increase score and move it back to top
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        # Move player left
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-PLAYER_SPEED, 0)

        # Move player right
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(PLAYER_SPEED, 0)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.weight = 1
        self.image = None
        self.rect = None
        self.reset_position()

    def load_coin_image(self):
        # Load different image depending on coin weight
        if self.weight == 1:
            self.image = pygame.image.load("Coin.png").convert_alpha()
        elif self.weight == 2:
            self.image = pygame.image.load("Coins.png").convert_alpha()
        else:
            self.image = pygame.image.load("MoreCoins.png").convert_alpha()

        self.image = pygame.transform.smoothscale(self.image, (40, 40))

    def reset_position(self):
        # Randomly choose coin weight
        self.weight = random.randint(1, 3)

        # Load image for chosen weight
        self.load_coin_image()

        # Random position on the road
        x = random.randint(40, SCREEN_WIDTH - 40)
        y = random.randint(-600, -50)

        # Create rect after image is loaded
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self):
        self.rect.move_ip(0, COIN_SPEED)

        # If coin leaves screen, create new random coin
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()


# Setting up sprites
P1 = Player()
E1 = Enemy()
C1 = Coin()

# Creating sprite groups
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# Adding new user event for general difficulty increase
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # General small speed increase with time
        if event.type == INC_SPEED:
            COIN_SPEED += 0.1

    # Draw background
    DISPLAYSURF.blit(background, (0, 0))

    # Draw score
    scores = font_small.render("Score: " + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10, 10))

    # Draw collected coins
    coin_text = font_small.render("Coins: " + str(COIN_COUNT), True, BLACK)
    DISPLAYSURF.blit(coin_text, (SCREEN_WIDTH - 100, 10))

    # Draw current enemy speed
    speed_text = font_small.render("Enemy speed: " + str(round(ENEMY_SPEED, 1)), True, BLACK)
    DISPLAYSURF.blit(speed_text, (10, 35))

    # Move and draw sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # If player collects coin, add coin weight
    if pygame.sprite.spritecollideany(P1, coins):
        COIN_COUNT += C1.weight
        C1.reset_position()

        # Increase enemy speed when player earns N coins
        if COIN_COUNT >= next_speedup:
            ENEMY_SPEED += 1
            next_speedup += COINS_FOR_SPEEDUP

    # If player crashes into enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        crash_sound.play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()

        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)