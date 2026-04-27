import pygame
import datetime
import os


class MickeyClock:
    def __init__(self, width=1365, height=768):
        pygame.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Mickey Clock")

        self.clock = pygame.time.Clock()

        base_path = os.path.dirname(__file__)
        images_path = os.path.join(base_path, "images")

        self.background = pygame.image.load(
            os.path.join(images_path, "clock.png")
        ).convert_alpha()

        self.mickey = pygame.image.load(
            os.path.join(images_path, "mUmrP.png")
        ).convert_alpha()

        self.left_hand = pygame.image.load(
            os.path.join(images_path, "left_hand.png")
        ).convert_alpha()

        self.right_hand = pygame.image.load(
            os.path.join(images_path, "right_hand.png")
        ).convert_alpha()

        self.background = pygame.transform.scale(self.background, (self.width, self.height))

        mickey_width = 650
        mickey_height = 760
        self.mickey = pygame.transform.scale(self.mickey, (mickey_width, mickey_height))

        self.mickey_x = 360
        self.mickey_y = 5

        self.screen_pivot = (690, 360)

        self.left_hand_pivot = (189, 62)
        self.right_hand_pivot = (236, 88)

    def blit_rotate(self, surface, image, screen_pivot, image_pivot, angle):
        image_rect = image.get_rect(
            topleft=(screen_pivot[0] - image_pivot[0], screen_pivot[1] - image_pivot[1])
        )

        offset_center_to_pivot = pygame.math.Vector2(screen_pivot) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        rotated_center = (
            screen_pivot[0] - rotated_offset.x,
            screen_pivot[1] - rotated_offset.y
        )

        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=rotated_center)

        surface.blit(rotated_image, rotated_rect)

    def get_time_angles(self):
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        minute_angle = -(minutes * 6)
        second_angle = -(seconds * 6)

        return minute_angle, second_angle

    def draw(self):
        minute_angle, second_angle = self.get_time_angles()

        self.screen.fill((255, 255, 255))
        self.screen.blit(self.background, (0, 0))

        # Сначала Микки
        self.screen.blit(self.mickey, (self.mickey_x, self.mickey_y))

        # Потом руки поверх него
        self.blit_rotate(
            self.screen,
            self.right_hand,
            self.screen_pivot,
            self.right_hand_pivot,
            minute_angle
        )

        self.blit_rotate(
            self.screen,
            self.left_hand,
            self.screen_pivot,
            self.left_hand_pivot,
            second_angle
        )

        pygame.display.flip()

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw()
            self.clock.tick(60)

        pygame.quit()