import pygame

from game.core import settings
from game.models.entities import lane_x


class Renderer:
    def __init__(self):
        self.font_big = pygame.font.SysFont("consolas", 36)
        self.font_small = pygame.font.SysFont("consolas", 20)
        self.player_image = self._load_player_image()
        self.obstacle_image = self._load_image(settings.OBSTACLE_IMG, settings.OBSTACLE_SIZE)
        self.background_image = self._load_background()
        self._player_rot_cache = {}
        self.medal_images = {
            "bronze": self._load_image(settings.MEDAL_BRONZE_IMG, settings.MEDAL_SIZE),
            "silver": self._load_image(settings.MEDAL_SILVER_IMG, settings.MEDAL_SIZE),
            "gold": self._load_image(settings.MEDAL_GOLD_IMG, settings.MEDAL_SIZE),
        }

    def _load_player_image(self):
        if settings.PLAYER_IMG.exists():
            image = pygame.image.load(settings.PLAYER_IMG).convert_alpha()
            h = settings.PLAYER_RENDER_HEIGHT
            scale = h / image.get_height()
            w = int(image.get_width() * scale)
            return pygame.transform.smoothscale(image, (w, h))
        return None

    def _load_image(self, path, size):
        if path.exists():
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(image, size)
        return None

    def _load_background(self):
        if settings.BACKGROUND_IMG.exists():
            image = pygame.image.load(settings.BACKGROUND_IMG).convert()
            return pygame.transform.smoothscale(image, (settings.WIDTH, settings.HEIGHT))
        return None

    def draw_background(self, screen):
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(settings.BG_COLOR)

    def draw_player(self, screen, player):
        x, y, w, h = player.rect
        if self.player_image:
            px = x + w // 2 - self.player_image.get_width() // 2
            py = y + h - self.player_image.get_height()
            angle = int(round(player.tilt))
            if abs(angle) > 0:
                rotated = self._player_rot_cache.get(angle)
                if rotated is None:
                    rotated = pygame.transform.rotate(self.player_image, angle)
                    self._player_rot_cache[angle] = rotated
                rect = rotated.get_rect(center=(px + self.player_image.get_width() // 2, py + self.player_image.get_height() // 2))
                screen.blit(rotated, rect.topleft)
            else:
                screen.blit(self.player_image, (px, py))
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

    def draw_medals(self, screen, medals):
        for medal in medals:
            x, y, w, h = medal.rect
            image = self.medal_images.get(medal.kind)
            if image:
                screen.blit(image, (x, y))
            else:
                pygame.draw.circle(screen, (240, 210, 80), (x + w // 2, y + h // 2), w // 2)

    def draw_ui(self, screen, score, medal_score, speed):
        score_text = self.font_small.render(f"Score: {score}", True, settings.UI_COLOR)
        medal_text = self.font_small.render(f"Medals: {medal_score}", True, settings.UI_COLOR)
        speed_text = self.font_small.render(f"Speed: {speed:.1f}", True, settings.UI_COLOR)
        screen.blit(score_text, (16, 12))
        screen.blit(medal_text, (16, 36))
        screen.blit(speed_text, (16, 60))

    def draw_title(self, screen, title, subtitle):
        t = self.font_big.render(title, True, settings.UI_COLOR)
        s = self.font_small.render(subtitle, True, settings.UI_COLOR)
        screen.blit(t, (settings.WIDTH // 2 - t.get_width() // 2, settings.HEIGHT // 2 - 60))
        screen.blit(s, (settings.WIDTH // 2 - s.get_width() // 2, settings.HEIGHT // 2))

    def draw_lane_marker(self, screen, lane_index):
        x = lane_x(lane_index)
        pygame.draw.circle(screen, (90, 110, 140), (x, settings.HEIGHT - 20), 6)
