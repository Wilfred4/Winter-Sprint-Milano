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
        self.menu_image = self._load_menu_background()
        self.menu_button_image = self._load_menu_button()
        self._menu_button_cache = {}
        self._bg_offset = 0.0
        self._bg_height = self.background_image.get_height() if self.background_image else 0
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
            scale = settings.WIDTH / image.get_width()
            height = max(1, int(image.get_height() * scale))
            return pygame.transform.smoothscale(image, (settings.WIDTH, height))
        return None

    def _load_menu_background(self):
        if settings.MENU_BG_IMG.exists():
            image = pygame.image.load(settings.MENU_BG_IMG).convert()
            return pygame.transform.smoothscale(image, (settings.WIDTH, settings.HEIGHT))
        return None

    def _load_menu_button(self):
        if settings.MENU_BUTTON_IMG.exists():
            return pygame.image.load(settings.MENU_BUTTON_IMG).convert_alpha()
        return None

    def draw_background(self, screen, scroll_speed=0.0):
        if self.background_image:
            self._bg_offset = (self._bg_offset - scroll_speed) % self._bg_height
            y = -self._bg_offset
            screen.blit(self.background_image, (0, y))
            if y + self._bg_height < settings.HEIGHT:
                screen.blit(self.background_image, (0, y + self._bg_height))
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
        shadow = settings.UI_SHADOW
        screen.blit(self.font_small.render(f"Score: {score}", True, shadow), (17, 13))
        screen.blit(self.font_small.render(f"Medals: {medal_score}", True, shadow), (17, 37))
        screen.blit(self.font_small.render(f"Speed: {speed:.1f}", True, shadow), (17, 61))
        screen.blit(score_text, (16, 12))
        screen.blit(medal_text, (16, 36))
        screen.blit(speed_text, (16, 60))

    def draw_menu(self, screen, start_rect, start_hovered, quit_rect, quit_hovered):
        if self.menu_image:
            screen.blit(self.menu_image, (0, 0))
        else:
            screen.fill(settings.BG_COLOR)
        # glass style buttons
        self._draw_glass_button(screen, start_rect, start_hovered, "START")
        self._draw_glass_button(screen, quit_rect, quit_hovered, "QUIT")

    def _draw_glass_button(self, screen, rect, hovered, label):
        if self.menu_button_image:
            key = (rect.width, rect.height)
            img = self._menu_button_cache.get(key)
            if img is None:
                img = pygame.transform.smoothscale(self.menu_button_image, (rect.width, rect.height))
                self._menu_button_cache[key] = img
            if hovered:
                scale = 1.04
                w = int(rect.width * scale)
                h = int(rect.height * scale)
                hover_key = ("hover", w, h)
                hover_img = self._menu_button_cache.get(hover_key)
                if hover_img is None:
                    hover_img = pygame.transform.smoothscale(img, (w, h))
                    self._menu_button_cache[hover_key] = hover_img
                screen.blit(hover_img, (rect.centerx - w // 2, rect.centery - h // 2))
            else:
                screen.blit(img, rect.topleft)
        else:
            pygame.draw.rect(screen, (20, 20, 25), rect, border_radius=12)
            pygame.draw.rect(screen, (240, 240, 240), rect, 2, border_radius=12)
        text = self.font_big.render(label, True, (245, 255, 255))
        shadow = self.font_big.render(label, True, (20, 40, 60))
        screen.blit(shadow, (rect.centerx - text.get_width() // 2 + 2, rect.centery - text.get_height() // 2 + 2))
        screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    def draw_title(self, screen, title, subtitle):
        t = self.font_big.render(title, True, settings.UI_COLOR)
        s = self.font_small.render(subtitle, True, settings.UI_COLOR)
        screen.blit(t, (settings.WIDTH // 2 - t.get_width() // 2, settings.HEIGHT // 2 - 60))
        screen.blit(s, (settings.WIDTH // 2 - s.get_width() // 2, settings.HEIGHT // 2))

    def draw_lane_marker(self, screen, lane_index):
        x = lane_x(lane_index)
        pygame.draw.circle(screen, (90, 110, 140), (x, settings.HEIGHT - 20), 6)
