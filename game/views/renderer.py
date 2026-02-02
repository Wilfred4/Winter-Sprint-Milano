import pygame

from game.core import settings
from game.models.entities import lane_x


class Renderer:
    def __init__(self):
        self.font_big = pygame.font.SysFont("consolas", 36)
        self.font_small = pygame.font.SysFont("consolas", 20)
        self.shooting_bg = None
        if settings.SHOOTING_BG_IMAGE:
            try:
                img = pygame.image.load(settings.SHOOTING_BG_IMAGE).convert()
                self.shooting_bg = pygame.transform.scale(img, (settings.WIDTH, settings.HEIGHT))
            except Exception:
                self.shooting_bg = None

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
        pygame.draw.rect(screen, settings.PLAYER_COLOR, (x, y, w, h), border_radius=10)
        pygame.draw.rect(screen, (180, 180, 190), (x + 10, y + 16, w - 20, h - 32), border_radius=6)

    def draw_obstacles(self, screen, obstacles):
        for obstacle in obstacles:
            x, y, w, h = obstacle.rect
            pygame.draw.rect(screen, settings.OBSTACLE_COLOR, (x, y, w, h), border_radius=8)

    def draw_ui(self, screen, score, speed, lives=None):
        score_text = self.font_small.render(f"Score: {score}", True, settings.UI_COLOR)
        speed_text = self.font_small.render(f"Speed: {speed:.1f}", True, settings.UI_COLOR)
        screen.blit(score_text, (16, 12))
        screen.blit(speed_text, (16, 36))
        if lives is not None:
            lives_text = self.font_small.render(f"Lives: {lives}", True, settings.UI_COLOR)
            screen.blit(lives_text, (16, 60))

    def draw_title(self, screen, title, subtitle):
        t = self.font_big.render(title, True, settings.UI_COLOR)
        s = self.font_small.render(subtitle, True, settings.UI_COLOR)
        screen.blit(t, (settings.WIDTH // 2 - t.get_width() // 2, settings.HEIGHT // 2 - 60))
        screen.blit(s, (settings.WIDTH // 2 - s.get_width() // 2, settings.HEIGHT // 2))

    def draw_lane_marker(self, screen, lane_index):
        x = lane_x(lane_index)
        pygame.draw.circle(screen, (90, 110, 140), (x, settings.HEIGHT - 20), 6)

    def draw_shooting(self, screen, target_positions, targets_hit, cursor_x, shots_left, time_left_s, lives):
        if self.shooting_bg is not None:
            screen.blit(self.shooting_bg, (0, 0))
        else:
            screen.fill(settings.SHOOTING_BG_COLOR)

        title = self.font_big.render("Phase de tir", True, (0, 0, 0))
        screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, 40))

        cy = settings.SHOOTING_TARGET_Y
        for x, hit in zip(target_positions, targets_hit):
            tx, ty = int(x), int(cy)
            pygame.draw.circle(screen, (0, 0, 0), (tx, ty), settings.SHOOTING_TARGET_RADIUS)
            if hit:
                pygame.draw.circle(
                    screen,
                    settings.SHOOTING_BG_COLOR,
                    (tx, ty),
                    max(6, settings.SHOOTING_TARGET_RADIUS - 6),
                )

        cx, cy = int(cursor_x), int(settings.SHOOTING_TARGET_Y)
        pygame.draw.circle(screen, (220, 40, 40), (cx, cy), settings.SHOOTING_CURSOR_RADIUS, 2)
        pygame.draw.line(screen, (220, 40, 40), (cx - 14, cy), (cx + 14, cy), 2)
        pygame.draw.line(screen, (220, 40, 40), (cx, cy - 14), (cx, cy + 14), 2)

        shots_text = self.font_small.render(f"Balles: {shots_left}", True, (0, 0, 0))
        time_text = self.font_small.render(f"Temps: {time_left_s}s", True, (0, 0, 0))
        lives_text = self.font_small.render(f"Vies: {lives}", True, (0, 0, 0))
        hint_text = self.font_small.render("Espace pour tirer", True, (0, 0, 0))
        screen.blit(shots_text, (16, 12))
        screen.blit(time_text, (16, 36))
        screen.blit(lives_text, (16, 60))
        screen.blit(hint_text, (16, settings.HEIGHT - 36))
