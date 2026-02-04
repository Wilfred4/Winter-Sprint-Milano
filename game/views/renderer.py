import time

import pygame
import math

from game.core import settings
from game.models.entities import lane_x, TargetState


class Renderer:
    def __init__(self):
        # Polices adaptées pour 1920x1080
        self.font_big = pygame.font.SysFont("consolas", 56)
        self.font_medium = pygame.font.SysFont("consolas", 42)
        self.font_small = pygame.font.SysFont("consolas", 32)
        self.font_tiny = pygame.font.SysFont("consolas", 24)
        self.player_image = self._load_player_image()
        self.hockey_player_image = self._load_hockey_player_image()
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

        # Images phase tir
        self.shooting_bg_image = self._load_fullscreen_image(settings.SHOOTING_BG_IMG)
        self.target_image = self._load_image(settings.TARGET_IMG, settings.TARGET_SIZE)
        self.target_hit_image = None  # On teintera l'image
        self.target_miss_image = None
        self.sight_image = self._load_image(settings.SIGHT_IMG, settings.SIGHT_SIZE)

        # Images compteur
        self.countdown_images = {
            3: self._load_countdown_image(settings.COUNTDOWN_3_IMG),
            2: self._load_countdown_image(settings.COUNTDOWN_2_IMG),
            1: self._load_countdown_image(settings.COUNTDOWN_1_IMG),
            "start": self._load_countdown_image(settings.COUNTDOWN_START_IMG),
        }

    def _load_fullscreen_image(self, path):
        if path.exists():
            image = pygame.image.load(path).convert()
            return pygame.transform.smoothscale(image, (settings.WIDTH, settings.HEIGHT))
        return None

    def _load_countdown_image(self, path):
        if path.exists():
            image = pygame.image.load(path).convert_alpha()
            # Taille du compteur pour 1920x1080
            return pygame.transform.smoothscale(image, (500, 350))
        return None

    def _load_player_image(self):
        if settings.PLAYER_IMG.exists():
            image = pygame.image.load(settings.PLAYER_IMG).convert_alpha()
            h = settings.PLAYER_RENDER_HEIGHT
            scale = h / image.get_height()
            w = int(image.get_width() * scale)
            return pygame.transform.smoothscale(image, (w, h))
        return None

    def _load_hockey_player_image(self):
        if settings.PLAYER_IMG.exists():
            image = pygame.image.load(settings.PLAYER_IMG).convert_alpha()
            return image
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

    def draw_menu(self, screen, buttons, title="CHOISIR UN JEU"):
        if self.menu_image:
            screen.blit(self.menu_image, (0, 0))
        else:
            # fond dégradé moderne
            for y in range(settings.HEIGHT):
                t = y / max(1, settings.HEIGHT)
                r = int(14 + 20 * t)
                g = int(20 + 40 * t)
                b = int(36 + 80 * t)
                pygame.draw.line(screen, (r, g, b), (0, y), (settings.WIDTH, y))

            # halo central
            glow = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow, (80, 130, 255, 40), (settings.WIDTH // 2, 220), 320)
            screen.blit(glow, (0, 0))

        title_text = self.font_big.render(title, True, (240, 245, 255))
        shadow = self.font_big.render(title, True, (10, 20, 40))
        screen.blit(shadow, (settings.WIDTH // 2 - title_text.get_width() // 2 + 3, 110 + 3))
        screen.blit(title_text, (settings.WIDTH // 2 - title_text.get_width() // 2, 110))

        subtitle = self.font_small.render("Biathlon ou Hockey 1v1", True, (200, 210, 225))
        screen.blit(subtitle, (settings.WIDTH // 2 - subtitle.get_width() // 2, 170))

        for rect, hovered, label in buttons:
            self._draw_modern_button(screen, rect, hovered, label)

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

    def _draw_modern_button(self, screen, rect, hovered, label):
        base = (34, 48, 74)
        border = (120, 160, 220)
        glow = (90, 140, 230, 80)
        if hovered:
            base = (44, 64, 96)
            border = (160, 200, 255)

        # ombre
        shadow_rect = rect.move(0, 6)
        pygame.draw.rect(screen, (10, 14, 22), shadow_rect, border_radius=18)

        # halo
        if hovered:
            halo = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(halo, glow, halo.get_rect(), border_radius=22)
            screen.blit(halo, (rect.x - 10, rect.y - 10))

        pygame.draw.rect(screen, base, rect, border_radius=18)
        pygame.draw.rect(screen, border, rect, 3, border_radius=18)

        text = self.font_big.render(label, True, (245, 250, 255))
        screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    def draw_title(self, screen, title, subtitle):
        t = self.font_big.render(title, True, settings.UI_COLOR)
        s = self.font_small.render(subtitle, True, settings.UI_COLOR)
        screen.blit(t, (settings.WIDTH // 2 - t.get_width() // 2, settings.HEIGHT // 2 - 60))
        screen.blit(s, (settings.WIDTH // 2 - s.get_width() // 2, settings.HEIGHT // 2))

    def draw_lane_marker(self, screen, lane_index):
        x = lane_x(lane_index)
        pygame.draw.circle(screen, (90, 110, 140), (x, settings.HEIGHT - 20), 6)

    # === PHASE TIR ===

    def draw_shooting_background(self, screen):
        """Fond pour la phase de tir"""
        if self.shooting_bg_image:
            screen.blit(self.shooting_bg_image, (0, 0))
        else:
            screen.fill(settings.SHOOTING_BG_COLOR)
            pygame.draw.rect(screen, (240, 245, 255), (0, 450, settings.WIDTH, settings.HEIGHT - 450))
            pygame.draw.line(screen, (150, 170, 190), (0, 450), (settings.WIDTH, 450), 3)

    def draw_targets(self, screen, targets):
        """Dessine les cibles avec les images"""
        for target in targets:
            x, y, w, h = target.rect

            if self.target_image:
                # Utiliser l'image
                if target.state == TargetState.NORMAL:
                    screen.blit(self.target_image, (x, y))
                elif target.state == TargetState.HIT:
                    # Teinter en vert
                    tinted = self.target_image.copy()
                    tinted.fill((100, 255, 100, 0), special_flags=pygame.BLEND_RGBA_ADD)
                    screen.blit(tinted, (x, y))
                else:  # MISSED
                    # Teinter en rouge
                    tinted = self.target_image.copy()
                    tinted.fill((255, 100, 100, 0), special_flags=pygame.BLEND_RGBA_ADD)
                    screen.blit(tinted, (x, y))
            else:
                # Fallback : dessiner des cercles
                cx, cy = x + w // 2, y + h // 2
                if target.state == TargetState.NORMAL:
                    color = settings.TARGET_COLOR
                elif target.state == TargetState.HIT:
                    color = settings.TARGET_HIT_COLOR
                else:
                    color = settings.TARGET_MISS_COLOR
                pygame.draw.circle(screen, color, (cx, cy), w // 2)
                pygame.draw.circle(screen, (255, 255, 255), (cx, cy), int(w * 0.35))
                pygame.draw.circle(screen, color, (cx, cy), int(w * 0.15))

    def draw_sight(self, screen, sight):
        """Dessine le viseur avec l'image"""
        x = int(sight.x)
        y = int(sight.y)

        if self.sight_image:
            screen.blit(self.sight_image, (x, y))
        else:
            # Fallback : dessiner le viseur manuellement
            size = sight.width
            cx = x + size // 2
            cy = y + size // 2
            pygame.draw.line(screen, settings.SIGHT_COLOR, (x, cy), (x + size, cy), 3)
            pygame.draw.line(screen, settings.SIGHT_COLOR, (cx, y), (cx, y + size), 3)
            pygame.draw.circle(screen, settings.SIGHT_COLOR, (cx, cy), size // 2, 3)
            pygame.draw.circle(screen, settings.SIGHT_COLOR, (cx, cy), 4)

    def draw_countdown(self, screen, step):
        """Dessine l'image du compte à rebours (3, 2, 1, start)"""
        image = self.countdown_images.get(step)
        if image:
            x = settings.WIDTH // 2 - image.get_width() // 2
            y = settings.HEIGHT // 2 - image.get_height() // 2
            screen.blit(image, (x, y))
        else:
            # Fallback : texte
            text = "START" if step == "start" else str(step)
            font = pygame.font.SysFont("consolas", 120, bold=True)
            rendered = font.render(text, True, (255, 80, 80))
            screen.blit(rendered, (settings.WIDTH // 2 - rendered.get_width() // 2,
                                   settings.HEIGHT // 2 - rendered.get_height() // 2))

    def draw_shooting_ui(self, screen, shots_remaining, targets_hit, score, lives):
        """UI pour la phase de tir"""
        # Tirs restants
        shots_text = self.font_big.render(f"Tirs: {shots_remaining}", True, settings.UI_COLOR)
        screen.blit(shots_text, (settings.WIDTH // 2 - shots_text.get_width() // 2, 30))

        # Cibles touchées
        hit_text = self.font_small.render(f"Touchées: {targets_hit}/{settings.NUM_TARGETS}", True, settings.UI_COLOR)
        screen.blit(hit_text, (settings.WIDTH // 2 - hit_text.get_width() // 2, 100))

        # Score (gauche)
        score_text = self.font_small.render(f"Score: {score}", True, settings.UI_COLOR)
        screen.blit(score_text, (30, 20))

        # Vies (droite)
        self.draw_lives(screen, lives)

        # Instruction
        instruction = self.font_small.render("ESPACE pour tirer", True, settings.UI_COLOR)
        screen.blit(instruction, (settings.WIDTH // 2 - instruction.get_width() // 2, settings.HEIGHT - 80))

    def draw_lives(self, screen, lives):
        """Affiche les vies (cœurs)"""
        heart_size = 45  # Taille pour 1920x1080
        max_display = 5
        start_x = settings.WIDTH - 40 - (heart_size + 12) * min(max_display, max(0, lives + 1))

        for i in range(max(0, lives + 1)):
            if i >= max_display:
                break
            x = start_x + i * (heart_size + 12)
            self._draw_heart(screen, x, 20, heart_size, (220, 60, 60))

        if lives < 0:
            self._draw_heart(screen, settings.WIDTH - 40 - heart_size, 20, heart_size, (150, 150, 160), filled=False)

    def _draw_heart(self, screen, x, y, size, color, filled=True):
        """Dessine un cœur"""
        points = [
            (x + size // 2, y + size),
            (x, y + size // 3),
            (x + size // 4, y),
            (x + size // 2, y + size // 4),
            (x + 3 * size // 4, y),
            (x + size, y + size // 3),
        ]
        if filled:
            pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (100, 50, 50), points, 2)

    def draw_ski_ui(self, screen, score, medal_score, lives, time_to_shooting):
        """UI pour la phase ski avec vies et compte à rebours circulaire"""
        shadow = settings.UI_SHADOW
        score_text = self.font_small.render(f"Score: {score}", True, settings.UI_COLOR)
        medal_text = self.font_small.render(f"Médailles: {medal_score}", True, settings.UI_COLOR)

        # Positions pour 1920x1080
        screen.blit(self.font_small.render(f"Score: {score}", True, shadow), (32, 22))
        screen.blit(self.font_small.render(f"Médailles: {medal_score}", True, shadow), (32, 62))
        screen.blit(score_text, (30, 20))
        screen.blit(medal_text, (30, 60))

        # Compte à rebours circulaire (centre)
        self.draw_circular_timer(screen, time_to_shooting, settings.SHOOTING_INTERVAL)

        # Vies (droite)
        self.draw_lives(screen, lives)

    def draw_circular_timer(self, screen, time_remaining, total_time):
        """Dessine un compte à rebours circulaire"""
        cx, cy = settings.WIDTH // 2, 60
        radius = 50  # Plus grand pour 1920x1080
        thickness = 8

        # Fond du cercle (gris)
        pygame.draw.circle(screen, (80, 80, 90), (cx, cy), radius, thickness)

        # Arc de progression
        progress = max(0, time_remaining / total_time)
        if progress > 0:
            # Couleur selon le temps restant
            if progress > 0.5:
                color = (80, 180, 80)  # Vert
            elif progress > 0.25:
                color = (220, 180, 60)  # Orange
            else:
                color = (220, 80, 80)  # Rouge

            # Dessiner l'arc
            start_angle = math.pi / 2  # Commence en haut
            end_angle = start_angle + (2 * math.pi * progress)
            rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
            pygame.draw.arc(screen, color, rect, start_angle, end_angle, thickness)

        # Texte au centre
        seconds = max(0, int(time_remaining / 1000))
        timer_text = self.font_small.render(f"{seconds}", True, settings.UI_COLOR)
        screen.blit(timer_text, (cx - timer_text.get_width() // 2, cy - timer_text.get_height() // 2))

    def draw_player_blinking(self, screen, player):
        """Dessine le joueur avec effet clignotant si invincible"""
        if player.is_invincible():
            if int(pygame.time.get_ticks() / 100) % 2 == 0:
                return  # Ne pas dessiner (effet clignotant)
        self.draw_player(screen, player)

    # === HOCKEY ===

    def draw_hockey_background(self, screen, rink_rect):
        screen.fill(settings.HOCKEY_RINK_COLOR)
        # glace bleutée
        pygame.draw.rect(screen, (200, 222, 242), rink_rect, border_radius=18)
        pygame.draw.rect(screen, (160, 190, 220), rink_rect, 6, border_radius=18)
        pygame.draw.rect(screen, settings.HOCKEY_RINK_LINE, rink_rect, 3, border_radius=18)

        # flocons légers
        for i in range(80):
            x = rink_rect.left + (i * 37) % max(1, rink_rect.width)
            y = rink_rect.top + (i * 53) % max(1, rink_rect.height)
            pygame.draw.circle(screen, (230, 240, 250), (x, y), 2)

        cx = rink_rect.centerx
        pygame.draw.line(screen, settings.HOCKEY_RINK_LINE,
                         (cx, rink_rect.top + 10), (cx, rink_rect.bottom - 10), 3)

        pygame.draw.circle(screen, settings.HOCKEY_RINK_LINE, rink_rect.center, 90, 3)

        goal_h = settings.HOCKEY_GOAL_HEIGHT
        goal_top = rink_rect.centery - goal_h // 2
        pygame.draw.rect(screen, settings.HOCKEY_GOAL_COLOR,
                         (rink_rect.left - 12, goal_top, 12, goal_h))
        pygame.draw.rect(screen, settings.HOCKEY_GOAL_COLOR,
                         (rink_rect.right, goal_top, 12, goal_h))

    def draw_hockey_player(self, screen, player, color, use_sprite=False):
        x, y, w, h = player.rect
        if use_sprite and self.hockey_player_image:
            img = self.hockey_player_image
            scale = h / img.get_height()
            new_w = max(1, int(img.get_width() * scale))
            new_h = max(1, int(img.get_height() * scale))
            sprite = pygame.transform.smoothscale(img, (new_w, new_h))
            sx = x + w // 2 - new_w // 2
            sy = y + h // 2 - new_h // 2
            screen.blit(sprite, (sx, sy))
            return
        pygame.draw.rect(screen, color, (x, y, w, h), border_radius=18)
        pygame.draw.rect(screen, (30, 30, 30), (x, y, w, h), 3, border_radius=18)

    def draw_hockey_puck(self, screen, puck, trail=None):
        if trail:
            for i, (tx, ty) in enumerate(trail):
                alpha = max(0, 200 - i * 12)
                radius = max(2, puck.radius - i // 3)
                surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                # halo bleu
                pygame.draw.circle(surf, (120, 170, 255, alpha), (radius + 2, radius + 2), radius + 1)
                # coeur plus clair
                pygame.draw.circle(surf, (200, 230, 255, alpha), (radius + 2, radius + 2), radius)
                screen.blit(surf, (int(tx - radius - 2), int(ty - radius - 2)))

        pygame.draw.circle(screen, settings.HOCKEY_PUCK_COLOR, (int(puck.x), int(puck.y)), puck.radius)
        pygame.draw.circle(screen, (30, 30, 30), (int(puck.x), int(puck.y)), puck.radius, 3)

    def draw_hockey_ui(self, screen, player_score, ai_score, time_left_ms):
        score_text = self.font_medium.render(f"JOUEUR {player_score}  -  {ai_score} IA", True, (245, 245, 250))
        screen.blit(score_text, (settings.WIDTH // 2 - score_text.get_width() // 2, 30))

        subtitle = self.font_small.render("Premier à 3 buts", True, (200, 210, 220))
        screen.blit(subtitle, (settings.WIDTH // 2 - subtitle.get_width() // 2, 80))

        hint = self.font_tiny.render("ZQSD / FLÈCHES pour bouger - M pour menu", True, (200, 200, 210))
        screen.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2, settings.HEIGHT - 60))

    def draw_hockey_goal_text(self, screen, text):
        msg = self.font_big.render(text, True, (255, 215, 0))
        screen.blit(msg, (settings.WIDTH // 2 - msg.get_width() // 2, settings.HEIGHT // 2 - 40))

    def draw_hockey_over(self, screen, result_text, player_score, ai_score):
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

    # === EFFETS VISUELS ===

    def draw_flash(self, screen, color, alpha):
        """Dessine un flash coloré sur l'écran"""
        if alpha <= 0:
            return
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((*color, min(255, int(alpha))))
        screen.blit(overlay, (0, 0))

    def draw_floating_text(self, screen, texts):
        """Dessine des textes flottants animés
        texts: liste de dicts {text, x, y, color, alpha, scale}
        """
        for t in texts:
            if t['alpha'] <= 0:
                continue
            font_size = int(24 * t.get('scale', 1.0))
            font = pygame.font.SysFont("consolas", font_size, bold=True)
            text_surface = font.render(t['text'], True, t['color'])
            text_surface.set_alpha(int(t['alpha']))
            screen.blit(text_surface, (int(t['x']) - text_surface.get_width() // 2, int(t['y'])))

    # === GAME OVER AMÉLIORÉ ===

    def draw_game_over(self, screen, score, medal_score, distance, best_score, animation_progress):
        """Écran Game Over amélioré avec animations"""
        # Fond semi-transparent
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Animation de zoom pour le titre
        title_scale = min(1.0, animation_progress * 2)
        title_y = settings.HEIGHT // 2 - 140

        # Titre "GAME OVER"
        title_size = int(48 * title_scale)
        if title_size > 0:
            title_font = pygame.font.SysFont("consolas", title_size, bold=True)
            title = title_font.render("GAME OVER", True, (255, 80, 80))
            # Ombre
            shadow = title_font.render("GAME OVER", True, (80, 20, 20))
            screen.blit(shadow, (settings.WIDTH // 2 - title.get_width() // 2 + 3, title_y + 3))
            screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, title_y))

        # Statistiques (apparaissent progressivement)
        if animation_progress > 0.3:
            stats_alpha = min(255, int((animation_progress - 0.3) * 400))
            self._draw_stat_box(screen, settings.WIDTH // 2, settings.HEIGHT // 2 - 40,
                               "SCORE", str(score), (255, 255, 255), stats_alpha)

        if animation_progress > 0.5:
            stats_alpha = min(255, int((animation_progress - 0.5) * 400))
            self._draw_stat_box(screen, settings.WIDTH // 2, settings.HEIGHT // 2 + 20,
                               "MÉDAILLES", str(medal_score), (255, 215, 0), stats_alpha)

        if animation_progress > 0.7:
            stats_alpha = min(255, int((animation_progress - 0.7) * 400))
            self._draw_stat_box(screen, settings.WIDTH // 2, settings.HEIGHT // 2 + 80,
                               "DISTANCE", f"{int(distance)}m", (100, 200, 255), stats_alpha)

        # Meilleur score
        if animation_progress > 0.9 and best_score > 0:
            best_alpha = min(255, int((animation_progress - 0.9) * 1000))
            if score >= best_score:
                best_text = self.font_medium.render("NOUVEAU RECORD !", True, (255, 215, 0))
            else:
                best_text = self.font_small.render(f"Meilleur: {best_score}", True, (180, 180, 180))
            best_text.set_alpha(best_alpha)
            screen.blit(best_text, (settings.WIDTH // 2 - best_text.get_width() // 2, settings.HEIGHT // 2 + 130))

        # Instruction pour rejouer
        if animation_progress >= 1.0:
            # Effet de pulsation
            pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() / 200)
            instruction = self.font_small.render("Appuie sur ENTER pour rejouer", True, (200, 200, 200))
            instruction.set_alpha(int(255 * pulse))
            screen.blit(instruction, (settings.WIDTH // 2 - instruction.get_width() // 2, settings.HEIGHT - 80))

            menu = self.font_small.render("M pour menu", True, (200, 200, 200))
            menu.set_alpha(int(255 * pulse))
            screen.blit(menu, (settings.WIDTH // 2 - menu.get_width() // 2, settings.HEIGHT - 40))

    def _draw_stat_box(self, screen, cx, cy, label, value, color, alpha):
        """Dessine une boîte de statistique"""
        # Label
        label_text = self.font_tiny.render(label, True, (150, 150, 150))
        label_text.set_alpha(alpha)
        screen.blit(label_text, (cx - label_text.get_width() // 2, cy - 12))

        # Valeur
        value_text = self.font_medium.render(value, True, color)
        value_text.set_alpha(alpha)
        screen.blit(value_text, (cx - value_text.get_width() // 2, cy + 5))
