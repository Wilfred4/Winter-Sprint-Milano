import pygame

from game.core import settings
from game.models.entities import lane_x


class Renderer:
    def __init__(self):
        self.font_big = pygame.font.SysFont("consolas", 36)
        self.font_small = pygame.font.SysFont("consolas", 20)
        self.player_image = self._load_image(settings.PLAYER_IMG, settings.PLAYER_SIZE)
        self.obstacle_image = self._load_image(settings.OBSTACLE_IMG, settings.OBSTACLE_SIZE)

    def _load_image(self, path, size):
        if path.exists():
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(image, size)
        return None

    def draw_background(self, screen):
        screen.fill(settings.BG_COLOR)
        pygame.draw.rect(
            screen,
            settings.ROAD_COLOR,
            (settings.LANE_PADDING - 20, 0, settings.WIDTH - 2 * settings.LANE_PADDING + 40, settings.HEIGHT),
        )
        lane_width = (settings.WIDTH - 2 * settings.LANE_PADDING) // settings.LANES
        for i in range(1, settings.LANES):
            x = settings.LANE_PADDING + i * lane_width
            pygame.draw.line(screen, settings.LANE_LINE, (x, 0), (x, settings.HEIGHT), 2)

    def draw_player(self, screen, player):
        x, y, w, h = player.rect
        if self.player_image:
            screen.blit(self.player_image, (x, y))
            return
        pygame.draw.rect(screen, settings.PLAYER_COLOR, (x, y, w, h), border_radius=10)
        pygame.draw.rect(screen, (180, 180, 190), (x + 10, y + 16, w - 20, h - 32), border_radius=6)

    def draw_obstacles(self, screen, obstacles):
        for obstacle in obstacles:
            x, y, w, h = obstacle.rect
            if self.obstacle_image:
                screen.blit(self.obstacle_image, (x, y))
            else:
                pygame.draw.rect(screen, settings.OBSTACLE_COLOR, (x, y, w, h), border_radius=8)

    def draw_ui(self, screen, score, speed):
        score_text = self.font_small.render(f"Score: {score}", True, settings.UI_COLOR)
        speed_text = self.font_small.render(f"Speed: {speed:.1f}", True, settings.UI_COLOR)
        screen.blit(score_text, (16, 12))
        screen.blit(speed_text, (16, 36))

    def draw_title(self, screen, title, subtitle):
        t = self.font_big.render(title, True, settings.UI_COLOR)
        s = self.font_small.render(subtitle, True, settings.UI_COLOR)
        screen.blit(t, (settings.WIDTH // 2 - t.get_width() // 2, settings.HEIGHT // 2 - 60))
        screen.blit(s, (settings.WIDTH // 2 - s.get_width() // 2, settings.HEIGHT // 2))

    def draw_lane_marker(self, screen, lane_index):
        x = lane_x(lane_index)
        pygame.draw.circle(screen, (90, 110, 140), (x, settings.HEIGHT - 20), 6)
