import pygame

from game.core import settings


class HockeyRenderer:
    def __init__(self):
        self.font_big = pygame.font.SysFont("consolas", 56)
        self.font_medium = pygame.font.SysFont("consolas", 42)
        self.font_small = pygame.font.SysFont("consolas", 32)
        self.font_tiny = pygame.font.SysFont("consolas", 24)
        self.player_sprite = self._load_player_sprite("player_hockey.png")
        self.ai_sprite = self._load_player_sprite("player_hockey2.png")
        self.logo = self._load_logo()
        self.banner_height = 70
    def _load_logo(self):
        path = settings.ASSETS_DIR / "logo.png"
        if path.exists():
            image = pygame.image.load(path).convert_alpha()
            return image
        return None


    def _load_player_sprite(self, filename):
        path = settings.ASSETS_DIR / filename
        if path.exists():
            image = pygame.image.load(path).convert_alpha()
            try:
                bg_color = image.get_at((0, 0))
                image.set_colorkey(bg_color)
            except Exception:
                pass
            return image
        return None

    def _load_banner(self):
        return None

    def draw_background(self, screen, rink_rect):
        # Fond du stade (bleu nuit)
        screen.fill((10, 14, 24))

        # Zone haute: bannière sobre codée (fond noir + logo)
        top_band_h = max(1, max(rink_rect.top, self.banner_height))
        banner_rect = pygame.Rect(0, 0, settings.WIDTH, top_band_h)
        pygame.draw.rect(screen, (8, 10, 14), banner_rect)
        pygame.draw.line(screen, (25, 28, 36), (0, top_band_h - 2), (settings.WIDTH, top_band_h - 2), 2)

        # Texte à gauche
        title = self.font_medium.render("HOCKEY 1V1", True, (230, 235, 245))
        screen.blit(title, (24, (top_band_h - title.get_height()) // 2))

        # Logo en haut à droite sans déformation
        if self.logo:
            max_h = min(86, top_band_h - 8)
            scale = max_h / self.logo.get_height()
            logo_w = max(1, int(self.logo.get_width() * scale))
            logo_h = max(1, int(self.logo.get_height() * scale))
            logo = pygame.transform.smoothscale(self.logo, (logo_w, logo_h))
            screen.blit(logo, (settings.WIDTH - logo_w - 20, (top_band_h - logo_h) // 2))

        # Bandeau haut supprimé pour un rendu épuré

        # Bordure extérieure du stade
        outer_border = pygame.Rect(rink_rect.left - 20, rink_rect.top - 20,
                                   rink_rect.width + 40, rink_rect.height + 40)
        pygame.draw.rect(screen, (20, 26, 36), outer_border, border_radius=20)

        # Bandes de la patinoire
        pygame.draw.rect(screen, (160, 28, 42), rink_rect, 16, border_radius=18)
        pygame.draw.rect(screen, (230, 195, 80), rink_rect, 4, border_radius=18)

        # Glace
        ice_rect = pygame.Rect(rink_rect.left + 10, rink_rect.top + 10,
                               rink_rect.width - 20, rink_rect.height - 20)
        pygame.draw.rect(screen, (245, 250, 255), ice_rect, border_radius=12)

        # Brillance glace
        shine_surface = pygame.Surface((ice_rect.width, ice_rect.height), pygame.SRCALPHA)
        for i in range(0, ice_rect.height, 36):
            alpha = 10 + (i % 80) // 10
            pygame.draw.line(shine_surface, (200, 220, 240, alpha),
                             (0, i), (ice_rect.width, i), 2)
        screen.blit(shine_surface, (ice_rect.left, ice_rect.top))

        # Vignette légère pour profondeur
        vignette = pygame.Surface((ice_rect.width, ice_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (0, 0, 0, 25), vignette.get_rect(), border_radius=12)
        screen.blit(vignette, (ice_rect.left, ice_rect.top))

        cx = rink_rect.centerx
        cy = rink_rect.centery

        # Lignes de jeu
        blue_left = rink_rect.left + rink_rect.width // 3
        blue_right = rink_rect.right - rink_rect.width // 3
        pygame.draw.line(screen, (40, 130, 215),
                         (blue_left, rink_rect.top + 20), (blue_left, rink_rect.bottom - 20), 6)
        pygame.draw.line(screen, (40, 130, 215),
                         (blue_right, rink_rect.top + 20), (blue_right, rink_rect.bottom - 20), 6)
        pygame.draw.line(screen, (200, 30, 45),
                         (cx, rink_rect.top + 20), (cx, rink_rect.bottom - 20), 6)

        pygame.draw.circle(screen, (40, 130, 215), (cx, cy), 85, 5)
        pygame.draw.circle(screen, (190, 30, 45), (cx, cy), 18)

        # Points mise au jeu
        faceoff_color = (200, 30, 45)
        faceoff_positions = [
            (blue_left, cy - 120),
            (blue_left, cy + 120),
            (blue_right, cy - 120),
            (blue_right, cy + 120),
        ]
        for fx, fy in faceoff_positions:
            pygame.draw.circle(screen, faceoff_color, (fx, fy), 15)
            pygame.draw.circle(screen, (0, 100, 200), (fx, fy), 40, 3)

        # Buts
        goal_h = settings.HOCKEY_GOAL_HEIGHT
        goal_top = cy - goal_h // 2
        goal_width = 20

        goal_left_rect = pygame.Rect(rink_rect.left - goal_width, goal_top, goal_width, goal_h)
        pygame.draw.rect(screen, (255, 50, 50), goal_left_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), goal_left_rect, 3, border_radius=5)

        for i in range(0, goal_h, 12):
            pygame.draw.line(screen, (220, 220, 230),
                             (rink_rect.left - goal_width + 3, goal_top + i),
                             (rink_rect.left - 3, goal_top + i), 1)
        for i in range(0, goal_width, 8):
            pygame.draw.line(screen, (220, 220, 230),
                             (rink_rect.left - goal_width + i, goal_top + 3),
                             (rink_rect.left - goal_width + i, goal_top + goal_h - 3), 1)

        goal_right_rect = pygame.Rect(rink_rect.right, goal_top, goal_width, goal_h)
        pygame.draw.rect(screen, (255, 50, 50), goal_right_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), goal_right_rect, 3, border_radius=5)

        for i in range(0, goal_h, 12):
            pygame.draw.line(screen, (220, 220, 230),
                             (rink_rect.right + 3, goal_top + i),
                             (rink_rect.right + goal_width - 3, goal_top + i), 1)
        for i in range(0, goal_width, 8):
            pygame.draw.line(screen, (220, 220, 230),
                             (rink_rect.right + i, goal_top + 3),
                             (rink_rect.right + i, goal_top + goal_h - 3), 1)

    def draw_player(self, screen, player, color, sprite=None, active=False):
        x, y, w, h = player.rect
        if sprite:
            scale = h / sprite.get_height()
            new_w = max(1, int(sprite.get_width() * scale))
            new_h = max(1, int(sprite.get_height() * scale))
            img = pygame.transform.smoothscale(sprite, (new_w, new_h))
            sx = x + w // 2 - new_w // 2
            sy = y + h // 2 - new_h // 2
            screen.blit(img, (sx, sy))
            if active:
                self._draw_active_cursor(screen, sx + new_w // 2, sy - 10)
            return

        shadow_rect = (x - 2, y + 2, w, h)
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=18)
        pygame.draw.rect(screen, color, (x, y, w, h), border_radius=18)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 4, border_radius=18)
        if active:
            self._draw_active_cursor(screen, x + w // 2, y - 10)

    def _draw_active_cursor(self, screen, cx, cy):
        # Petit curseur triangulaire type FIFA
        size = 10
        points = [(cx, cy), (cx - size, cy - size * 2), (cx + size, cy - size * 2)]
        pygame.draw.polygon(screen, (255, 215, 0), points)
        pygame.draw.polygon(screen, (30, 30, 30), points, 2)

    def draw_puck(self, screen, puck, trail=None):
        if trail:
            for i, (tx, ty) in enumerate(trail):
                alpha = max(0, 180 - i * 12)
                radius = max(2, puck.radius - i // 3)
                surf = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 150, 50, alpha), (radius + 3, radius + 3), radius + 2)
                pygame.draw.circle(surf, (255, 220, 100, alpha), (radius + 3, radius + 3), radius)
                screen.blit(surf, (int(tx - radius - 3), int(ty - radius - 3)))

        shadow_surf = pygame.Surface((puck.radius * 2 + 8, puck.radius * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 100), (puck.radius + 4, puck.radius + 6), puck.radius + 2)
        screen.blit(shadow_surf, (int(puck.x - puck.radius - 4), int(puck.y - puck.radius - 4)))

        glow_surf = pygame.Surface((puck.radius * 2 + 10, puck.radius * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 200, 50, 60), (puck.radius + 5, puck.radius + 5), puck.radius + 4)
        screen.blit(glow_surf, (int(puck.x - puck.radius - 5), int(puck.y - puck.radius - 5)))

        pygame.draw.circle(screen, (30, 30, 35), (int(puck.x), int(puck.y)), puck.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(puck.x), int(puck.y)), puck.radius, 3)
        pygame.draw.circle(screen, (255, 150, 50), (int(puck.x), int(puck.y)), puck.radius // 3)

    def draw_ui(self, screen, player_score, ai_score):
        panel_width = 500
        panel_height = 90
        panel_x = settings.WIDTH // 2 - panel_width // 2
        panel_y = 130

        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 25, 35, 220), (0, 0, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(panel_surf, (255, 215, 0), (0, 0, panel_width, panel_height), 3, border_radius=15)
        screen.blit(panel_surf, (panel_x, panel_y))

        score_text = self.font_big.render(f"{player_score}  -  {ai_score}", True, (255, 215, 0))
        screen.blit(score_text, (settings.WIDTH // 2 - score_text.get_width() // 2, panel_y + 15))

        player_label = self.font_tiny.render("JOUEUR", True, (100, 200, 255))
        ai_label = self.font_tiny.render("IA", True, (255, 100, 100))
        screen.blit(player_label, (panel_x + 50, panel_y + 65))
        screen.blit(ai_label, (panel_x + panel_width - 80, panel_y + 65))

        hint_bg = pygame.Surface((settings.WIDTH, 50), pygame.SRCALPHA)
        hint_bg.fill((0, 0, 0, 160))
        screen.blit(hint_bg, (0, settings.HEIGHT - 50))

        hint = self.font_tiny.render("ZQSD/FLÈCHES: Bouger  |  ESPACE: Tirer  |  M: Menu", True, (220, 230, 240))
        screen.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2, settings.HEIGHT - 35))

    def draw_goal_text(self, screen, text):
        msg = self.font_big.render(text, True, (255, 215, 0))
        screen.blit(msg, (settings.WIDTH // 2 - msg.get_width() // 2, settings.HEIGHT // 2 - 40))

    def draw_over(self, screen, result_text, player_score, ai_score):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.font_big.render(result_text, True, (255, 215, 0))
        screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, settings.HEIGHT // 2 - 120))

        score = self.font_medium.render(f"JOUEUR {player_score}  -  {ai_score} IA", True, (240, 240, 245))
        screen.blit(score, (settings.WIDTH // 2 - score.get_width() // 2, settings.HEIGHT // 2 - 30))

        replay = self.font_small.render("ENTER pour rejouer", True, (200, 200, 210))
        menu = self.font_small.render("M pour menu", True, (200, 200, 210))
        screen.blit(replay, (settings.WIDTH // 2 - replay.get_width() // 2, settings.HEIGHT // 2 + 60))
        screen.blit(menu, (settings.WIDTH // 2 - menu.get_width() // 2, settings.HEIGHT // 2 + 110))
