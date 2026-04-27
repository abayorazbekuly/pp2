import pygame


class MovingBallGame:
    def __init__(self, width=800, height=600):
        pygame.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Moving Ball")

        self.clock = pygame.time.Clock()

        self.ball_radius = 25
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.step = 20

        self.white = (255, 255, 255)
        self.red = (255, 0, 0)

    def move_ball(self, dx, dy):
        new_x = self.ball_x + dx
        new_y = self.ball_y + dy

        if self.ball_radius <= new_x <= self.width - self.ball_radius:
            self.ball_x = new_x

        if self.ball_radius <= new_y <= self.height - self.ball_radius:
            self.ball_y = new_y

    def draw(self):
        self.screen.fill(self.white)
        pygame.draw.circle(
            self.screen,
            self.red,
            (self.ball_x, self.ball_y),
            self.ball_radius
        )
        pygame.display.flip()

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move_ball(-self.step, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_ball(self.step, 0)
                    elif event.key == pygame.K_UP:
                        self.move_ball(0, -self.step)
                    elif event.key == pygame.K_DOWN:
                        self.move_ball(0, self.step)

            self.draw()
            self.clock.tick(60)

        pygame.quit()