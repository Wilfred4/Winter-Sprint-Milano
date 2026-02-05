import math
import random

import pygame

from game.core import settings
from game.scenes.base import Scene
from game.hockey.entities import HockeyPlayer, Puck
from game.hockey.renderer import HockeyRenderer
from game.hockey.sound import HockeySound


class HockeyScene(Scene):
    """Mode Hockey 1v1 contre l'IA."""

    def __init__(self, game):
        super().__init__(game)
        pygame.mixer.music.stop()  # Couper la musique du menu

        self.renderer = HockeyRenderer()
        self.sfx = HockeySound()

        # Patinoire
        margin = settings.HOCKEY_RINK_MARGIN
        top_margin = max(margin, min(self.renderer.banner_height + 10, 120))
        self.rink_rect = pygame.Rect(
            margin, top_margin,
            settings.WIDTH - 2 * margin,
            settings.HEIGHT - top_margin - margin
        )

        # Positions de départ
        cx, cy = self.rink_rect.center
        self.player_start = (self.rink_rect.left + 120, cy)
        self.ai_start = (self.rink_rect.right - 120, cy)

        self.player = HockeyPlayer(*self.player_start)
        self.ai = HockeyPlayer(*self.ai_start)
        self.puck = Puck(cx, cy)

        # Scores et état
        self.player_score = 0
        self.ai_score = 0
        self.goal_timer = 0
        self.goal_text = None
        self.paused = False
        self.puck_trail = []

        # Cooldowns
        self.shoot_cooldown = 0
        self.ai_shoot_cooldown = 0
        self.ai_react_timer = 0
        self.serve_timer = 0
        self.serve_vx = 0
        self.serve_vy = 0

        self._serve_puck()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            elif event.key == pygame.K_m:
                self.sfx.stop()
                from game.scenes.menu import MenuScene
                self.game.change_scene(MenuScene(self.game))

    def update(self, dt):
        if self.paused:
            return

        # Pause après un but
        if self.goal_timer > 0:
            self.goal_timer -= dt
            if self.goal_timer <= 0:
                self.goal_timer = 0
                self.goal_text = None
                self._serve_puck()
            return

        # Attente avant le service
        if self.serve_timer > 0:
            self.serve_timer -= dt
            if self.serve_timer <= 0:
                self.serve_timer = 0
                self.puck.vx = self.serve_vx
                self.puck.vy = self.serve_vy
            return

        # Fin du match ?
        if self.player_score >= settings.HOCKEY_MAX_SCORE or self.ai_score >= settings.HOCKEY_MAX_SCORE:
            self.sfx.stop()
            self.game.change_scene(HockeyOverScene(self.game, self.player_score, self.ai_score))
            return

        dt_sec = min(dt / 1000.0, 0.05)

        # Mise à jour des cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.ai_shoot_cooldown > 0:
            self.ai_shoot_cooldown -= dt
        if self.ai_react_timer > 0:
            self.ai_react_timer -= dt

        shoot_pressed = self._update_player(dt_sec)
        ai_should_shoot = self._update_ai(dt_sec)

        self.puck.update(dt_sec)
        self._update_trail()

        self._handle_walls()
        self._handle_collision(self.player, shoot_pressed, is_ai=False)
        self._handle_collision(self.ai, ai_should_shoot, is_ai=True)

        self._check_goals()

    def _serve_puck(self):
        cx, cy = self.rink_rect.center
        self.puck.x = cx
        self.puck.y = cy
        self.serve_vx = random.choice([-580, 580])
        self.serve_vy = random.uniform(-120, 120)
        self.puck.vx = 0
        self.puck.vy = 0
        self.puck_trail = []
        self.sfx.play_whistle()
        self.serve_timer = settings.HOCKEY_SERVE_DELAY_MS

    def _reset_positions(self):
        self.player.x, self.player.y = self.player_start
        self.ai.x, self.ai.y = self.ai_start
        self.puck.x, self.puck.y = self.rink_rect.center
        self.puck.vx = 0
        self.puck.vy = 0
        self.puck_trail = []

    def _update_player(self, dt_sec):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # Normaliser la direction
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

        speed = settings.HOCKEY_PLAYER_SPEED
        new_x = self.player.x + dx * speed * dt_sec
        new_y = self.player.y + dy * speed * dt_sec

        # Rester dans la patinoire
        margin = 35
        new_x = max(self.rink_rect.left + margin, min(self.rink_rect.right - margin, new_x))
        new_y = max(self.rink_rect.top + margin, min(self.rink_rect.bottom - margin, new_y))

        self.player.x = new_x
        self.player.y = new_y

        return keys[pygame.K_SPACE]

    def _update_ai(self, dt_sec):
        center_x = self.rink_rect.centerx
        margin = 60

        # Vérifier si l'IA est coincée dans un coin
        near_left = self.ai.x < self.rink_rect.left + margin
        near_right = self.ai.x > self.rink_rect.right - margin
        near_top = self.ai.y < self.rink_rect.top + margin
        near_bottom = self.ai.y > self.rink_rect.bottom - margin
        in_corner = (near_left or near_right) and (near_top or near_bottom)

        # L'IA veut-elle tirer ?
        should_shoot = False
        dist_to_puck = math.hypot(self.puck.x - self.ai.x, self.puck.y - self.ai.y)
        if dist_to_puck < 75 and self.puck.x <= center_x + 10 and self.ai_shoot_cooldown <= 0 and self.ai_react_timer <= 0:
            should_shoot = True

        # Palet coincé dans un coin gauche ?
        puck_in_left_corner = (
            self.puck.x < self.rink_rect.left + margin + 20
            and (self.puck.y < self.rink_rect.top + margin + 20 or self.puck.y > self.rink_rect.bottom - margin - 20)
        )

        if in_corner or puck_in_left_corner:
            # Sortir du coin
            if near_left:
                self.ai.x = max(self.ai.x, self.rink_rect.left + margin + 40)
            if near_right:
                self.ai.x = min(self.ai.x, self.rink_rect.right - margin - 40)
            if near_top:
                self.ai.y = max(self.ai.y, self.rink_rect.top + margin + 40)
            if near_bottom:
                self.ai.y = min(self.ai.y, self.rink_rect.bottom - margin - 40)

            target_x = center_x + 60
            target_y = self.rink_rect.centery
            should_shoot = False
            if self.ai_shoot_cooldown <= 0:
                self.ai_shoot_cooldown = 300
                self.ai_react_timer = 250
        else:
            # Suivre le palet ou défendre
            if self.puck.x > self.rink_rect.right - 220:
                # Défendre le but
                target_x = self.rink_rect.right - 150
                target_y = self.rink_rect.centery + (self.puck.y - self.rink_rect.centery) * 0.6
            else:
                target_x = self.puck.x
                target_y = self.puck.y

        # Limiter aux bords
        target_x = max(self.rink_rect.left + 35, min(self.rink_rect.right - 35, target_x))
        target_y = max(self.rink_rect.top + 35, min(self.rink_rect.bottom - 35, target_y))

        # Déplacement vers la cible
        dx = target_x - self.ai.x
        dy = target_y - self.ai.y
        dist = math.hypot(dx, dy)

        if dist > 10:
            dx /= dist
            dy /= dist
            self.ai.x += dx * settings.HOCKEY_AI_REACTION_SPEED * dt_sec
            self.ai.y += dy * settings.HOCKEY_AI_REACTION_SPEED * dt_sec

        return should_shoot

    def _handle_walls(self):
        r = self.puck.radius
        goal_h = settings.HOCKEY_GOAL_HEIGHT / 2
        goal_y = self.rink_rect.centery

        # Rebonds haut/bas
        if self.puck.y - r < self.rink_rect.top:
            self.puck.y = self.rink_rect.top + r
            self.puck.vy = abs(self.puck.vy) * 0.9
        elif self.puck.y + r > self.rink_rect.bottom:
            self.puck.y = self.rink_rect.bottom - r
            self.puck.vy = -abs(self.puck.vy) * 0.9

        # Rebonds gauche/droite (sauf dans le but)
        in_goal = abs(self.puck.y - goal_y) < goal_h

        if self.puck.x - r < self.rink_rect.left and not in_goal:
            self.puck.x = self.rink_rect.left + r
            self.puck.vx = abs(self.puck.vx) * 0.9
        elif self.puck.x + r > self.rink_rect.right and not in_goal:
            self.puck.x = self.rink_rect.right - r
            self.puck.vx = -abs(self.puck.vx) * 0.9

    def _handle_collision(self, player, can_shoot, is_ai):
        dx = self.puck.x - player.x
        dy = self.puck.y - player.y
        dist = math.hypot(dx, dy)
        collision_dist = player.width / 2 + self.puck.radius

        if dist < collision_dist:
            if dist < 1:
                dx, dy = 1, 0
                dist = 1

            nx = dx / dist
            ny = dy / dist

            # Repousser le palet
            self.puck.x = player.x + nx * collision_dist
            self.puck.y = player.y + ny * collision_dist
            self.sfx.play_hit()

            if can_shoot:
                if is_ai and self.ai_shoot_cooldown <= 0:
                    # IA tire vers le but du joueur
                    target_x = self.rink_rect.left + 10
                    target_y = self.rink_rect.centery + random.uniform(-60, 60)
                    shoot_power = settings.HOCKEY_AI_SHOOT_POWER
                    self.ai_shoot_cooldown = settings.HOCKEY_AI_SHOOT_COOLDOWN_MS
                    self.ai_react_timer = 150
                elif not is_ai and self.shoot_cooldown <= 0:
                    # Joueur tire vers le but de l'IA
                    target_x = self.rink_rect.right - 10
                    target_y = self.rink_rect.centery
                    shoot_power = 1300
                    self.shoot_cooldown = 260
                else:
                    target_x = None

                if target_x is not None:
                    shoot_dx = target_x - player.x
                    shoot_dy = target_y - player.y
                    shoot_len = math.hypot(shoot_dx, shoot_dy)
                    if shoot_len > 0:
                        shoot_dx /= shoot_len
                        shoot_dy /= shoot_len
                    self.puck.vx = shoot_dx * shoot_power
                    self.puck.vy = shoot_dy * shoot_power
                    return

            # Frappe normale
            hit_power = 900
            if is_ai and nx > 0:
                nx = -abs(nx)  # L'IA ne tire pas vers son propre but
            self.puck.vx = nx * hit_power
            self.puck.vy = ny * hit_power

    def _check_goals(self):
        r = self.puck.radius
        goal_h = settings.HOCKEY_GOAL_HEIGHT / 2
        goal_y = self.rink_rect.centery
        left_line = self.rink_rect.left - 12
        right_line = self.rink_rect.right + 12
        min_speed = 200

        # But contre le joueur
        if self.puck.x - r <= left_line and self.puck.vx < -min_speed:
            if abs(self.puck.y - goal_y) < (goal_h - 12):
                self.ai_score += 1
                self.goal_text = "BUT IA !"
                self.goal_timer = settings.HOCKEY_GOAL_PAUSE
                self._reset_positions()
                self.sfx.play_goal()

        # But contre l'IA
        elif self.puck.x + r >= right_line and self.puck.vx > min_speed:
            if abs(self.puck.y - goal_y) < (goal_h - 12):
                self.player_score += 1
                self.goal_text = "BUT JOUEUR !"
                self.goal_timer = settings.HOCKEY_GOAL_PAUSE
                self._reset_positions()
                self.sfx.play_goal()

    def _update_trail(self):
        speed = math.hypot(self.puck.vx, self.puck.vy)
        if speed > 50:
            self.puck_trail.insert(0, (self.puck.x, self.puck.y))
            if len(self.puck_trail) > 15:
                self.puck_trail.pop()

    def render(self, screen):
        self.renderer.draw_background(screen, self.rink_rect)
        self.renderer.draw_puck(screen, self.puck, self.puck_trail)
        self.renderer.draw_player(screen, self.player, settings.HOCKEY_PLAYER_COLOR,
                                  sprite=self.renderer.player_sprite, active=True)
        self.renderer.draw_player(screen, self.ai, settings.HOCKEY_AI_COLOR,
                                  sprite=self.renderer.ai_sprite, active=False)
        self.renderer.draw_ui(screen, self.player_score, self.ai_score)

        if self.goal_text:
            self.renderer.draw_goal_text(screen, self.goal_text)

        if self.paused:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            pause_text = self.renderer.font_big.render("Pause", True, (255, 255, 255))
            screen.blit(pause_text, (settings.WIDTH // 2 - pause_text.get_width() // 2, settings.HEIGHT // 2))


class HockeyOverScene(Scene):
    """Ecran de fin de match Hockey."""

    def __init__(self, game, player_score, ai_score):
        super().__init__(game)
        self.player_score = player_score
        self.ai_score = ai_score
        self.renderer = HockeyRenderer()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.game.change_scene(HockeyScene(self.game))
            elif event.key == pygame.K_m:
                from game.scenes.menu import MenuScene
                self.game.change_scene(MenuScene(self.game))

    def update(self, dt):
        pass

    def render(self, screen):
        if self.player_score > self.ai_score:
            result = "VICTOIRE !"
        elif self.player_score < self.ai_score:
            result = "DEFAITE"
        else:
            result = "EGALITE"
        self.renderer.draw_over(screen, result, self.player_score, self.ai_score)
