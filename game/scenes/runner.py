import math
import random

import pygame

from game.core import settings
from game.controllers.input import InputController
from game.models.entities import Player, Target, Sight, TargetState, HockeyPlayer, Puck
from game.models.world import World
from game.scenes.base import Scene
from game.views.renderer import Renderer


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        # Boutons adaptés pour 1920x1080
        self.biathlon_button = pygame.Rect(0, 0, 520, 120)
        self.hockey_button = pygame.Rect(0, 0, 520, 120)
        self.quit_button = pygame.Rect(0, 0, 520, 120)

        self.biathlon_button.center = (settings.WIDTH // 2, settings.HEIGHT - 360)
        self.hockey_button.center = (settings.WIDTH // 2, settings.HEIGHT - 220)
        self.quit_button.center = (settings.WIDTH // 2, settings.HEIGHT - 100)

    def _start_biathlon(self):
        self.game.change_scene(CountdownScene(self.game, with_start=True))

    def _start_hockey(self):
        self.game.change_scene(HockeyScene(self.game))

    def handle_event(self, event):
        self.input.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                self._start_biathlon()
            if event.key == pygame.K_h:
                self._start_hockey()
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._start_biathlon()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.biathlon_button.collidepoint(event.pos):
                self._start_biathlon()
            if self.hockey_button.collidepoint(event.pos):
                self._start_hockey()
            if self.quit_button.collidepoint(event.pos):
                self.game.running = False

    def update(self, dt):
        left, right, jump, start = self.input.consume()
        if start or jump:
            self._start_biathlon()

    def render(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        biathlon_hovered = self.biathlon_button.collidepoint(mouse_pos)
        hockey_hovered = self.hockey_button.collidepoint(mouse_pos)
        quit_hovered = self.quit_button.collidepoint(mouse_pos)
        buttons = [
            (self.biathlon_button, biathlon_hovered, "BIATHLON"),
            (self.hockey_button, hockey_hovered, "HOCKEY 1V1"),
            (self.quit_button, quit_hovered, "QUITTER"),
        ]
        self.renderer.draw_menu(screen, buttons)


class CountdownScene(Scene):
    """Scène de décompte 3, 2, 1 (et Start optionnel)"""

    def __init__(self, game, with_start=False, next_scene_callback=None, player=None, world=None):
        super().__init__(game)
        self.renderer = Renderer()
        self.with_start = with_start
        self.next_scene_callback = next_scene_callback
        self.player = player
        self.world = world

        # Séquence : 3, 2, 1, (start)
        self.steps = [3, 2, 1]
        if with_start:
            self.steps.append("start")

        self.current_step = 0
        self.step_timer = 0

    def handle_event(self, event):
        pass

    def update(self, dt):
        self.step_timer += dt

        if self.step_timer >= settings.COUNTDOWN_STEP_DURATION:
            self.step_timer = 0
            self.current_step += 1

            if self.current_step >= len(self.steps):
                # Décompte terminé
                if self.next_scene_callback:
                    self.next_scene_callback()
                else:
                    # Par défaut : lancer le jeu
                    self.game.change_scene(SkiScene(self.game))

    def render(self, screen):
        # Fond
        self.renderer.draw_background(screen, 0)

        # Overlay semi-transparent
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        # Afficher le chiffre/texte actuel
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.renderer.draw_countdown(screen, step)


class SkiScene(Scene):
    """Phase SKI - Course d'esquive"""

    def __init__(self, game, player=None, world=None, from_shooting=False):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = player if player else Player()
        self.world = world if world else World()
        self.paused = False
        self.time_to_shooting = settings.SHOOTING_INTERVAL

        # Si on revient du tir, délai avant que les obstacles réapparaissent
        self.from_shooting = from_shooting
        self.obstacle_spawn_delay = settings.OBSTACLE_SPAWN_DELAY if from_shooting else 0

        # État du décompte avant le tir
        self.pre_shooting_countdown = False
        self.countdown_step = 3
        self.countdown_timer = 0

        # Effets visuels
        self.flash_color = None
        self.flash_alpha = 0
        self.floating_texts = []

    def handle_event(self, event):
        self.input.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused

    def update(self, dt):
        if self.paused:
            return

        # Gérer le décompte avant le tir
        if self.pre_shooting_countdown:
            self._update_pre_shooting_countdown(dt)
            return

        left, right, jump, _start = self.input.consume()
        if left:
            self.player.move_left()
        if right:
            self.player.move_right()
        if jump:
            self.player.jump()

        self.player.update(dt)

        # Mise à jour du délai de spawn après le tir
        if self.obstacle_spawn_delay > 0:
            self.obstacle_spawn_delay -= dt
            # Mettre à jour le monde mais sans spawn d'obstacles
            self.world.distance += dt * 0.001
            self.world.speed = settings.BASE_SCROLL_SPEED + self.world.distance * settings.SPEED_GROWTH * 500
            # Déplacer les obstacles existants
            for obstacle in self.world.obstacles:
                obstacle.update(self.world.speed)
            for medal in self.world.medals:
                medal.update(self.world.speed)
            self.world.obstacles = [o for o in self.world.obstacles if o.y - o.height < settings.HEIGHT + 40]
            self.world.medals = [m for m in self.world.medals if m.y - m.height < settings.HEIGHT + 40]
        else:
            self.world.update(dt)

        # Mise à jour des effets visuels
        self._update_effects(dt)

        # Timer pour la phase de tir
        self.time_to_shooting -= dt
        if self.time_to_shooting <= 0:
            # Lancer le décompte avant le tir
            self.pre_shooting_countdown = True
            self.countdown_step = 3
            self.countdown_timer = 0
            return

        # Score basé sur les obstacles évités
        for obstacle in self.world.obstacles:
            if not obstacle.passed and obstacle.y > self.player.y:
                obstacle.passed = True
                self.world.score += 1

        # Ramasser les médailles
        self.handle_medal_pickups()

        # Vérifier les collisions
        if self.check_collisions():
            self._trigger_flash((255, 0, 0), 150)
            if self.player.take_damage():
                self.game.change_scene(GameOverScene(self.game, self.world.score, self.world.medal_score, self.world.distance))

    def _update_pre_shooting_countdown(self, dt):
        """Met à jour le décompte avant la phase de tir"""
        self.countdown_timer += dt

        # Pendant le décompte, pas de spawn d'obstacles mais on continue à les déplacer
        self.world.distance += dt * 0.001
        for obstacle in self.world.obstacles:
            obstacle.update(self.world.speed)
        for medal in self.world.medals:
            medal.update(self.world.speed)
        self.world.obstacles = [o for o in self.world.obstacles if o.y - o.height < settings.HEIGHT + 40]
        self.world.medals = [m for m in self.world.medals if m.y - m.height < settings.HEIGHT + 40]

        if self.countdown_timer >= settings.COUNTDOWN_STEP_DURATION:
            self.countdown_timer = 0
            self.countdown_step -= 1

            if self.countdown_step <= 0:
                # Décompte terminé, passer à la phase de tir
                self.game.change_scene(ShootingScene(self.game, self.player, self.world))

    def _update_effects(self, dt):
        if self.flash_alpha > 0:
            self.flash_alpha -= dt * 0.3
            if self.flash_alpha < 0:
                self.flash_alpha = 0

        for t in self.floating_texts:
            t['y'] -= dt * 0.05
            t['alpha'] -= dt * 0.15
        self.floating_texts = [t for t in self.floating_texts if t['alpha'] > 0]

    def _trigger_flash(self, color, alpha):
        self.flash_color = color
        self.flash_alpha = alpha

    def _add_floating_text(self, text, x, y, color):
        self.floating_texts.append({
            'text': text,
            'x': x,
            'y': y,
            'color': color,
            'alpha': 255,
            'scale': 1.0
        })

    def check_collisions(self):
        if self.player.is_invincible():
            return False

        px, py, pw, ph = self.player.rect
        for obstacle in self.world.obstacles:
            ox, oy, ow, oh = obstacle.rect
            if px < ox + ow and px + pw > ox and py < oy + oh and py + ph > oy:
                return True
        return False

    def handle_medal_pickups(self):
        px, py, pw, ph = self.player.rect
        remaining = []
        for medal in self.world.medals:
            mx, my, mw, mh = medal.rect
            if px < mx + mw and px + pw > mx and py < my + mh and py + ph > my:
                points = settings.MEDAL_POINTS.get(medal.kind, 1)
                self.world.score += points
                self.world.medal_score += points
                color = (255, 215, 0) if medal.kind == "gold" else (200, 200, 200) if medal.kind == "silver" else (205, 127, 50)
                self._add_floating_text(f"+{points}", mx + mw // 2, my, color)
            else:
                remaining.append(medal)
        self.world.medals = remaining

    def render(self, screen):
        self.renderer.draw_background(screen, self.world.speed)
        self.renderer.draw_obstacles(screen, self.world.obstacles)
        self.renderer.draw_medals(screen, self.world.medals)
        self.renderer.draw_player_blinking(screen, self.player)
        self.renderer.draw_ski_ui(screen, self.world.score, self.world.medal_score, self.player.lives, self.time_to_shooting)
        self.renderer.draw_lane_marker(screen, self.player.lane)

        # Effets visuels
        self.renderer.draw_floating_text(screen, self.floating_texts)
        if self.flash_alpha > 0:
            self.renderer.draw_flash(screen, self.flash_color, self.flash_alpha)

        # Décompte avant le tir
        if self.pre_shooting_countdown:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            self.renderer.draw_countdown(screen, self.countdown_step)

        if self.paused:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            self.renderer.draw_title(screen, "Pause", "Echap pour reprendre")


class ShootingScene(Scene):
    """Phase TIR - Mini-jeu de précision"""

    def __init__(self, game, player, world):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = player
        self.world = world

        # Créer les 5 cibles (positionnées dans la bannière)
        self.targets = []
        margin = 200  # Marge sur les côtés
        total_width = settings.WIDTH - 2 * margin
        spacing = total_width // (settings.NUM_TARGETS - 1)
        for i in range(settings.NUM_TARGETS):
            x = margin + i * spacing - settings.TARGET_SIZE[0] // 2
            self.targets.append(Target(x=x))

        # Créer le viseur (au même niveau Y que les cibles)
        self.sight = Sight()

        self.current_target_index = 0
        self.shots_remaining = settings.NUM_TARGETS
        self.targets_hit = 0
        self.shot_cooldown = 0
        self.transition_timer = 0
        self.phase_complete = False

        # Effets visuels
        self.floating_texts = []
        self.flash_color = None
        self.flash_alpha = 0

    def handle_event(self, event):
        self.input.handle_event(event)

    def update(self, dt):
        left, right, jump, _start = self.input.consume()

        self._update_effects(dt)

        if self.shot_cooldown > 0:
            self.shot_cooldown -= dt

        if self.phase_complete:
            self.transition_timer += dt
            if self.transition_timer >= 1500:
                if self.targets_hit == settings.NUM_TARGETS:
                    self.player.lives += 1
                elif self.targets_hit < settings.MIN_TARGETS_TO_HIT:
                    if self.player.take_damage():
                        self.game.change_scene(GameOverScene(self.game, self.world.score, self.world.medal_score, self.world.distance))
                        return
                # Retourner au ski avec délai d'obstacles
                self.game.change_scene(SkiScene(self.game, self.player, self.world, from_shooting=True))
            return

        self.sight.update()

        if jump and self.shot_cooldown <= 0 and self.current_target_index < len(self.targets):
            self.shoot()
            self.shot_cooldown = 400

    def _update_effects(self, dt):
        if self.flash_alpha > 0:
            self.flash_alpha -= dt * 0.3
        for t in self.floating_texts:
            t['y'] -= dt * 0.05
            t['alpha'] -= dt * 0.15
        self.floating_texts = [t for t in self.floating_texts if t['alpha'] > 0]

    def shoot(self):
        target = self.targets[self.current_target_index]
        tx, ty, tw, th = target.rect

        if self.sight.is_on_target(target):
            target.state = TargetState.HIT
            self.targets_hit += 1
            self.world.score += settings.TARGET_HIT_BONUS
            self.floating_texts.append({
                'text': f"+{settings.TARGET_HIT_BONUS}",
                'x': tx + tw // 2,
                'y': ty - 20,
                'color': (80, 220, 80),
                'alpha': 255,
                'scale': 1.2
            })
            self.flash_color = (0, 255, 0)
            self.flash_alpha = 80
        else:
            target.state = TargetState.MISSED
            self.flash_color = (255, 0, 0)
            self.flash_alpha = 100

        self.current_target_index += 1
        self.shots_remaining -= 1

        if self.shots_remaining <= 0:
            self.phase_complete = True
            if self.targets_hit == settings.NUM_TARGETS:
                self.flash_color = (255, 215, 0)
                self.flash_alpha = 150

    def render(self, screen):
        self.renderer.draw_shooting_background(screen)
        self.renderer.draw_targets(screen, self.targets)
        if not self.phase_complete:
            self.renderer.draw_sight(screen, self.sight)
        self.renderer.draw_shooting_ui(screen, self.shots_remaining, self.targets_hit, self.world.score, self.player.lives)

        self.renderer.draw_floating_text(screen, self.floating_texts)
        if self.flash_alpha > 0:
            self.renderer.draw_flash(screen, self.flash_color, self.flash_alpha)

        if self.phase_complete:
            if self.targets_hit == settings.NUM_TARGETS:
                msg = f"PARFAIT ! {self.targets_hit}/{settings.NUM_TARGETS} (+1 vie)"
                color = (255, 215, 0)
            elif self.targets_hit >= settings.MIN_TARGETS_TO_HIT:
                msg = f"Bien ! {self.targets_hit}/{settings.NUM_TARGETS} cibles"
                color = (60, 180, 60)
            else:
                msg = f"Raté ! {self.targets_hit}/{settings.NUM_TARGETS} (-1 vie)"
                color = (200, 60, 60)
            text = self.renderer.font_big.render(msg, True, color)
            screen.blit(text, (settings.WIDTH // 2 - text.get_width() // 2, settings.HEIGHT - 180))


class HockeyScene(Scene):
    """Mode Hockey 1v1 contre l'IA"""

    def __init__(self, game):
        super().__init__(game)
        self.renderer = Renderer()
        margin = settings.HOCKEY_RINK_MARGIN
        self.rink_rect = pygame.Rect(margin, margin, settings.WIDTH - 2 * margin, settings.HEIGHT - 2 * margin)

        cx, cy = self.rink_rect.center
        self.player = HockeyPlayer(self.rink_rect.left + 140, cy)
        self.ai = HockeyPlayer(self.rink_rect.right - 140, cy)
        self.puck = Puck(cx, cy)

        self.player_score = 0
        self.ai_score = 0
        self.time_left = settings.HOCKEY_MATCH_TIME
        self.goal_timer = 0
        self.goal_text = None
        self.serve_direction = random.choice([-1, 1])
        self.paused = False
        self.player_hit_cooldown = 0
        self.ai_hit_cooldown = 0
        self.ai_target_x = self.ai.x
        self.ai_target_y = self.ai.y
        self.puck_trail = []
        self.puck_trail_max = 18

        self._serve_puck()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            if event.key == pygame.K_m:
                self.game.change_scene(MenuScene(self.game))

    def update(self, dt):
        if self.paused:
            return

        if self.player_hit_cooldown > 0:
            self.player_hit_cooldown -= dt
        if self.ai_hit_cooldown > 0:
            self.ai_hit_cooldown -= dt

        if self.goal_timer > 0:
            self.goal_timer -= dt
            if self.goal_timer <= 0:
                self.goal_timer = 0
                self.goal_text = None
                self._serve_puck()
            return

        if settings.HOCKEY_MATCH_TIME > 0:
            self.time_left -= dt

        if self.player_score >= settings.HOCKEY_MAX_SCORE or self.ai_score >= settings.HOCKEY_MAX_SCORE:
            self.game.change_scene(HockeyOverScene(self.game, self.player_score, self.ai_score))
            return

        dt_sec = max(0.0, dt / 1000.0)
        player_vx, player_vy = self._update_player(dt_sec)
        ai_vx, ai_vy = self._update_ai(dt_sec)

        self.puck.update(dt_sec)

        self._update_trail()

        self._handle_wall_collisions()
        self._handle_player_collision(self.player, player_vx, player_vy)
        self._handle_player_collision(self.ai, ai_vx, ai_vy)
        self._check_goals()

    def _serve_puck(self):
        self.puck.x, self.puck.y = self.rink_rect.center
        self.puck.vx = self.serve_direction * settings.HOCKEY_PUCK_SERVE_SPEED
        self.puck.vy = random.uniform(-120, 120)

    def _update_player(self, dt_sec):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

        speed = settings.HOCKEY_PLAYER_SPEED
        move_x = dx * speed * dt_sec
        move_y = dy * speed * dt_sec

        self._move_in_bounds(self.player, move_x, move_y, left_side=None)
        return move_x / dt_sec if dt_sec > 0 else 0, move_y / dt_sec if dt_sec > 0 else 0

    def _update_ai(self, dt_sec):
        # IA type Air Hockey améliorée avec anticipation
        lookahead = 0.25
        predicted_x = self.puck.x + self.puck.vx * lookahead
        predicted_y = self.puck.y + self.puck.vy * lookahead
        
        # Stratégie selon la position du palet
        if self.puck.x > self.rink_rect.centerx + 100:
            # Palet proche : attaquer
            target_x = predicted_x - 90
            target_y = predicted_y
        elif self.puck.x > self.rink_rect.centerx - 200:
            # Palet au centre : intercepter
            target_x = self.rink_rect.centerx + 180
            target_y = predicted_y
        else:
            # Palet loin : défendre le but
            target_x = self.rink_rect.right - 160
            goal_center = self.rink_rect.centery
            target_y = self._lerp(goal_center, predicted_y, 0.7)

        # Limites Y
        target_y = max(self.rink_rect.top + 80, min(self.rink_rect.bottom - 80, target_y))

        # Lissage pour mouvement fluide
        self.ai_target_x = self._lerp(self.ai_target_x, target_x, 0.18)
        self.ai_target_y = self._lerp(self.ai_target_y, target_y, 0.18)

        dx = self.ai_target_x - self.ai.x
        dy = self.ai_target_y - self.ai.y

        dist = math.hypot(dx, dy)
        if dist < 4:
            return 0, 0

        dx /= dist
        dy /= dist

        speed = settings.HOCKEY_AI_SPEED
        move_x = dx * speed * dt_sec
        move_y = dy * speed * dt_sec

        self._move_in_bounds(self.ai, move_x, move_y, left_side=False)
        return move_x / dt_sec if dt_sec > 0 else 0, move_y / dt_sec if dt_sec > 0 else 0

    def _move_in_bounds(self, player, move_x, move_y, left_side=True):
        half_w = player.width / 2
        half_h = player.height / 2
        min_x = self.rink_rect.left + half_w
        max_x = self.rink_rect.right - half_w

        if left_side is True:
            max_x = self.rink_rect.centerx - 30 - half_w
        elif left_side is False:
            min_x = self.rink_rect.centerx + 30 + half_w

        min_y = self.rink_rect.top + half_h
        max_y = self.rink_rect.bottom - half_h

        player.x = max(min_x, min(max_x, player.x + move_x))
        player.y = max(min_y, min(max_y, player.y + move_y))

    def _handle_wall_collisions(self):
        left = self.rink_rect.left
        right = self.rink_rect.right
        top = self.rink_rect.top
        bottom = self.rink_rect.bottom
        r = self.puck.radius

        if self.puck.y - r <= top:
            self.puck.y = top + r
            self.puck.vy = abs(self.puck.vy)
        if self.puck.y + r >= bottom:
            self.puck.y = bottom - r
            self.puck.vy = -abs(self.puck.vy)

        goal_top = self.rink_rect.centery - settings.HOCKEY_GOAL_HEIGHT / 2
        goal_bottom = self.rink_rect.centery + settings.HOCKEY_GOAL_HEIGHT / 2

        if self.puck.x - r <= left and not (goal_top <= self.puck.y <= goal_bottom):
            self.puck.x = left + r
            self.puck.vx = abs(self.puck.vx)
        if self.puck.x + r >= right and not (goal_top <= self.puck.y <= goal_bottom):
            self.puck.x = right - r
            self.puck.vx = -abs(self.puck.vx)

        # Garder le palet dans la zone sans tremblements
        self.puck.x = max(left + r, min(right - r, self.puck.x))
        self.puck.y = max(top + r, min(bottom - r, self.puck.y))

        if abs(self.puck.vx) < 5:
            self.puck.vx = 0
        if abs(self.puck.vy) < 5:
            self.puck.vy = 0

    def _handle_player_collision(self, player, pvx, pvy):
        if player is self.player and self.player_hit_cooldown > 0:
            return
        if player is self.ai and self.ai_hit_cooldown > 0:
            return
        if not self._circle_rect_collision(self.puck, player):
            return

        px, py = player.center
        dx = self.puck.x - px
        dy = self.puck.y - py
        dist = math.hypot(dx, dy)
        if dist == 0:
            dx, dy = 1, 0
            dist = 1

        nx, ny = dx / dist, dy / dist
        push = (player.width * 0.5 + self.puck.radius + 4)
        self.puck.x = px + nx * push
        self.puck.y = py + ny * push

        # éviter les rebonds quand le palet s'éloigne déjà
        rel_vx = self.puck.vx - pvx
        rel_vy = self.puck.vy - pvy
        approach = rel_vx * nx + rel_vy * ny
        if approach > 0:
            self.puck.vx *= 0.65
            self.puck.vy *= 0.65
            return

        # Tir plus naturel avec direction du joueur
        hit_strength = settings.HOCKEY_PUCK_HIT_SPEED
        self.puck.vx = nx * hit_strength + pvx * 0.35
        self.puck.vy = ny * hit_strength + pvy * 0.35

        if player is self.player:
            self.player_hit_cooldown = 120
        else:
            self.ai_hit_cooldown = 120

    @staticmethod
    def _lerp(a, b, t):
        return a + (b - a) * t

    def _circle_rect_collision(self, puck, player):
        rx, ry, rw, rh = player.rect
        closest_x = max(rx, min(puck.x, rx + rw))
        closest_y = max(ry, min(puck.y, ry + rh))
        dx = puck.x - closest_x
        dy = puck.y - closest_y
        return (dx * dx + dy * dy) <= (puck.radius * puck.radius)

    def _check_goals(self):
        left = self.rink_rect.left
        right = self.rink_rect.right
        r = self.puck.radius
        goal_top = self.rink_rect.centery - settings.HOCKEY_GOAL_HEIGHT / 2
        goal_bottom = self.rink_rect.centery + settings.HOCKEY_GOAL_HEIGHT / 2

        if self.puck.x - r <= left and goal_top <= self.puck.y <= goal_bottom:
            self.ai_score += 1
            self.goal_text = "BUT IA !"
            self._start_goal_pause(serve_direction=-1)

        if self.puck.x + r >= right and goal_top <= self.puck.y <= goal_bottom:
            self.player_score += 1
            self.goal_text = "BUT JOUEUR !"
            self._start_goal_pause(serve_direction=1)

    def _start_goal_pause(self, serve_direction):
        self.goal_timer = settings.HOCKEY_GOAL_PAUSE
        self.serve_direction = serve_direction
        self.puck.vx = 0
        self.puck.vy = 0
        self.puck.x, self.puck.y = self.rink_rect.center
        self.puck_trail = []

    def _update_trail(self):
        speed = math.hypot(self.puck.vx, self.puck.vy)
        if speed > 30:
            self.puck_trail.insert(0, (self.puck.x, self.puck.y))
        if len(self.puck_trail) > self.puck_trail_max:
            self.puck_trail = self.puck_trail[: self.puck_trail_max]

    def render(self, screen):
        self.renderer.draw_hockey_background(screen, self.rink_rect)
        self.renderer.draw_hockey_player(screen, self.player, settings.HOCKEY_PLAYER_COLOR, use_sprite=True)
        self.renderer.draw_hockey_player(screen, self.ai, settings.HOCKEY_AI_COLOR)
        self.renderer.draw_hockey_puck(screen, self.puck, self.puck_trail)
        self.renderer.draw_hockey_ui(screen, self.player_score, self.ai_score, self.time_left)

        if self.goal_text:
            self.renderer.draw_hockey_goal_text(screen, self.goal_text)

        if self.paused:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            self.renderer.draw_title(screen, "Pause", "Echap pour reprendre")


class HockeyOverScene(Scene):
    def __init__(self, game, player_score, ai_score):
        super().__init__(game)
        self.player_score = player_score
        self.ai_score = ai_score
        self.renderer = Renderer()
        self.restart = False
        self.back_to_menu = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.restart = True
            if event.key == pygame.K_m:
                self.back_to_menu = True

    def update(self, dt):
        if self.restart:
            self.game.change_scene(HockeyScene(self.game))
        if self.back_to_menu:
            self.game.change_scene(MenuScene(self.game))

    def render(self, screen):
        if self.player_score > self.ai_score:
            result = "VICTOIRE !"
        elif self.player_score < self.ai_score:
            result = "DÉFAITE"
        else:
            result = "ÉGALITÉ"
        self.renderer.draw_hockey_over(screen, result, self.player_score, self.ai_score)


class GameOverScene(Scene):
    def __init__(self, game, score, medal_score=0, distance=0):
        super().__init__(game)
        self.score = score
        self.medal_score = medal_score
        self.distance = distance
        self.input = InputController()
        self.renderer = Renderer()
        self.animation_time = 0
        self.can_restart = False
        self.back_to_menu = False

        self.best_score = self._load_best_score()
        if score > self.best_score:
            self._save_best_score(score)
            self.best_score = score

    def _load_best_score(self):
        try:
            with open(settings.ASSETS_DIR / "best_score.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0

    def _save_best_score(self, score):
        try:
            with open(settings.ASSETS_DIR / "best_score.txt", "w") as f:
                f.write(str(score))
        except:
            pass

    def handle_event(self, event):
        self.input.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m and self.can_restart:
                self.back_to_menu = True

    def update(self, dt):
        self.animation_time += dt / 1000
        if self.animation_time >= 1.5:
            self.can_restart = True

        left, right, jump, start = self.input.consume()
        if self.can_restart and (start or jump):
            self.game.change_scene(CountdownScene(self.game, with_start=True))
        if self.back_to_menu:
            self.game.change_scene(MenuScene(self.game))

    def render(self, screen):
        self.renderer.draw_background(screen)
        progress = min(1.0, self.animation_time / 1.5)
        self.renderer.draw_game_over(screen, self.score, self.medal_score, self.distance, self.best_score, progress)


# Alias pour compatibilité
PlayScene = SkiScene
