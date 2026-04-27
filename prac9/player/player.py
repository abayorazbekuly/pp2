import pygame
import os


class MusicPlayer:
    def __init__(self, width=800, height=400):
        pygame.init()
        pygame.mixer.init()

        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Music Player")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 22)

        base_path = os.path.dirname(__file__)
        music_path = os.path.join(base_path, "music")

        self.playlist = [
            os.path.join(music_path, "1.mp3"),
            os.path.join(music_path, "2.mp3"),
            os.path.join(music_path, "3.mp3"),
            os.path.join(music_path, "4.mp3"),
        ]

        self.current_index = 0
        self.is_playing = False

    def load_current_track(self):
        pygame.mixer.music.load(self.playlist[self.current_index])

    def play(self):
        self.load_current_track()
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_track(self):
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def get_current_track_name(self):
        return os.path.basename(self.playlist[self.current_index])

    def get_track_position(self):
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms < 0:
            return "00:00"
        seconds = pos_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return "%02d:%02d" % (minutes, seconds)

    def draw(self):
        self.screen.fill((230, 230, 230))

        title = self.font.render("Music Player", True, (0, 0, 0))
        track = self.small_font.render(
            "Current track: " + self.get_current_track_name(),
            True,
            (0, 0, 0)
        )
        status_text = "Playing" if self.is_playing else "Stopped"
        status = self.small_font.render(
            "Status: " + status_text,
            True,
            (0, 0, 0)
        )
        pos = self.small_font.render(
            "Position: " + self.get_track_position(),
            True,
            (0, 0, 0)
        )

        controls = self.small_font.render(
            "P - Play | S - Stop | N - Next | B - Previous | Q - Quit",
            True,
            (0, 0, 0)
        )

        self.screen.blit(title, (300, 40))
        self.screen.blit(track, (80, 120))
        self.screen.blit(status, (80, 170))
        self.screen.blit(pos, (80, 220))
        self.screen.blit(controls, (80, 300))

        pygame.display.flip()

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.play()
                    elif event.key == pygame.K_s:
                        self.stop()
                    elif event.key == pygame.K_n:
                        self.next_track()
                    elif event.key == pygame.K_b:
                        self.previous_track()
                    elif event.key == pygame.K_q:
                        running = False

            self.draw()
            self.clock.tick(30)

        pygame.quit()