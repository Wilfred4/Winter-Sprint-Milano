import pygame

from game.core import settings
from game.controllers.input import InputController
from game.models.entities import Player
from game.models.world import World
from game.scenes.base import Scene
from game.views.renderer import Renderer
from game.scenes.audio import MusicManager, SoundManager


class SkiScene(Scene):
    """Phase de ski - éviter les obstacles et ramasser les médailles."""

    def __init__(self, game, player=None, world=None, from_shooting=False):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = player if player else Player()
        self.world = world if world else World()
        self.paused = False
        self.time_to_shooting = settings.SHOOTING_INTERVAL

        self.from_shooting = from_shooting
        self.obstacle_spawn_delay = settings.OBSTACLE_SPAWN_DELAY if from_shooting else 0

        # Vider les obstacles si on revient du tir
        if from_shooting:
            self.world.obstacles.clear()

        # Préparation avant phase de tir
        self.pre_shooting_preparation = False
        self.preparation_timer = 0
        self.pre_shooting_countdown = False
        self.countdown_step = 3
        self.countdown_timer = 0

        # Effets visuels
        self.flash_color = None
        self.flash_alpha = 0
        self.floating_texts = []

        # Menu pause
        self.pause_selected = 0
        self.pause_buttons = [
            pygame.Rect(0, 0, 350, 80),
            pygame.Rect(0, 0, 350, 80),
            pygame.Rect(0, 0, 350, 80),
        ]
        self.pause_buttons[0].center = (settings.WIDTH // 2, settings.HEIGHT // 2 - 100)
        self.pause_buttons[1].center = (settings.WIDTH // 2, settings.HEIGHT // 2)
        self.pause_buttons[2].center = (settings.WIDTH // 2, settings.HEIGHT // 2 + 100)

    def handle_event(self, event):
        self.input.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
            self.pause_selected = 0

        if self.paused:
            self._handle_pause_event(event)

    def _handle_pause_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.pause_selected = (self.pause_selected - 1) % 3
            elif event.key == pygame.K_DOWN:
                self.pause_selected = (self.pause_selected + 1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._execute_pause_action(self.pause_selected)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn in enumerate(self.pause_buttons):
                if btn.collidepoint(event.pos):
                    self._execute_pause_action(i)
        elif event.type == pygame.MOUSEMOTION:
            for i, btn in enumerate(self.pause_buttons):
                if btn.collidepoint(event.pos):
                    self.pause_selected = i

    def _execute_pause_action(self, action):
        from game.scenes.menu import MenuScene

        if action == 0:
            self.paused = False
        elif action == 1:
            Renderer.reset_background_index()
            MusicManager.play_menu_music()
            self.game.change_scene(MenuScene(self.game))
        elif action == 2:
            self.game.running = False

    def update(self, dt):
        if self.paused:
            return

        left, right, jump, _ = self.input.consume()

        # Phase de préparation (piste vide avant le tir)
        if self.pre_shooting_preparation:
            self._update_pre_shooting_preparation(dt, left, right, jump)
            return

        # Countdown avant le tir
        if self.pre_shooting_countdown:
            self._update_pre_shooting_countdown(dt, left, right, jump)
            return

        # Mouvement du joueur
        if left:
            self.player.move_left()
        if right:
            self.player.move_right()
        if jump:
            self.player.jump()

        self.player.update(dt)
        self._update_world(dt)
        self._update_effects(dt)

        # Timer pour la phase de tir
        self.time_to_shooting -= dt
        if self.time_to_shooting <= 0:
            self.pre_shooting_preparation = True
            self.preparation_timer = 0
            self.world.obstacles.clear()
            return

        # Score quand on évite un obstacle
        for obstacle in self.world.obstacles:
            if not obstacle.passed and obstacle.y > self.player.y:
                obstacle.passed = True
                self.world.score += 1

        self._handle_medal_pickups()

        # Collision avec obstacle
        if self._check_collisions():
            self.flash_color = (255, 0, 0)
            self.flash_alpha = 150
            if self.player.take_damage():
                self._game_over()

    def _update_world(self, dt):
        if self.obstacle_spawn_delay > 0:
            self.obstacle_spawn_delay -= dt
            self.world.distance += dt * 0.001
            self.world.speed = min(
                settings.MAX_SCROLL_SPEED,
                settings.BASE_SCROLL_SPEED + self.world.distance * settings.SPEED_GROWTH
            )
            for obstacle in self.world.obstacles:
                obstacle.update(self.world.speed)
            for medal in self.world.medals:
                medal.update(self.world.speed)
            # Nettoyer les objets hors écran
            self.world.obstacles = [o for o in self.world.obstacles if o.y - o.height < settings.HEIGHT + 40]
            self.world.medals = [m for m in self.world.medals if m.y - m.height < settings.HEIGHT + 40]
        else:
            self.world.update(dt)

    def _update_pre_shooting_preparation(self, dt, left, right, jump):
        """Piste libre avant le countdown du tir."""
        self.preparation_timer += dt

        if left:
            self.player.move_left()
        if right:
            self.player.move_right()
        if jump:
            self.player.jump()
        self.player.update(dt)

        # Continuer à scroller
        self.world.distance += dt * 0.001
        self.world.speed = min(
            settings.MAX_SCROLL_SPEED,
            settings.BASE_SCROLL_SPEED + self.world.distance * settings.SPEED_GROWTH
        )

        for medal in self.world.medals:
            medal.update(self.world.speed)
        self.world.medals = [m for m in self.world.medals if m.y - m.height < settings.HEIGHT + 40]

        self._handle_medal_pickups()
        self._update_effects(dt)

        if self.preparation_timer >= settings.PRE_SHOOTING_CLEAR_TIME:
            self.pre_shooting_preparation = False
            self.pre_shooting_countdown = True
            self.countdown_step = 3
            self.countdown_timer = 0

    def _update_pre_shooting_countdown(self, dt, left, right, jump):
        """Countdown 3-2-1 avant le tir."""
        self.countdown_timer += dt

        if left:
            self.player.move_left()
        if right:
            self.player.move_right()
        if jump:
            self.player.jump()
        self.player.update(dt)

        self.world.distance += dt * 0.001
        for medal in self.world.medals:
            medal.update(self.world.speed)
        self.world.medals = [m for m in self.world.medals if m.y - m.height < settings.HEIGHT + 40]

        self._handle_medal_pickups()
        self._update_effects(dt)

        if self.countdown_timer >= settings.COUNTDOWN_STEP_DURATION:
            self.countdown_timer = 0
            self.countdown_step -= 1
            if self.countdown_step <= 0:
                from game.scenes.shooting import ShootingScene
                self.game.change_scene(ShootingScene(self.game, self.player, self.world))

    def _game_over(self):
        from game.scenes.gameover import GameOverScene
        self.game.change_scene(GameOverScene(
            self.game, self.world.score, self.world.medal_score, self.world.distance
        ))

    def _update_effects(self, dt):
        # Fade du flash
        if self.flash_alpha > 0:
            self.flash_alpha -= dt * 0.3
            if self.flash_alpha < 0:
                self.flash_alpha = 0

        # Animation des textes flottants
        for t in self.floating_texts:
            t['y'] -= dt * 0.05
            t['alpha'] -= dt * 0.15
        self.floating_texts = [t for t in self.floating_texts if t['alpha'] > 0]

    def _check_collisions(self):
        if self.player.is_invincible():
            return False

        px, py, pw, ph = self.player.rect
        for obstacle in self.world.obstacles:
            ox, oy, ow, oh = obstacle.rect
            # Test AABB classique
            if px < ox + ow and px + pw > ox and py < oy + oh and py + ph > oy:
                return True
        return False

    def _handle_medal_pickups(self):
        px, py, pw, ph = self.player.rect
        remaining = []

        for medal in self.world.medals:
            mx, my, mw, mh = medal.rect
            if px < mx + mw and px + pw > mx and py < my + mh and py + ph > my:
                # Médaille ramassée
                points = settings.MEDAL_POINTS.get(medal.kind, 1)
                self.world.score += points
                self.world.medal_score += points

                # Couleur selon le type
                if medal.kind == "gold":
                    color = (255, 215, 0)
                elif medal.kind == "silver":
                    color = (200, 200, 200)
                else:
                    color = (205, 127, 50)

                self.floating_texts.append({
                    'text': f"+{points}",
                    'x': mx + mw // 2,
                    'y': my,
                    'color': color,
                    'alpha': 255,
                    'scale': 1.0
                })
                SoundManager.play_coin()
            else:
                remaining.append(medal)

        self.world.medals = remaining

    def render(self, screen):
        self.renderer.draw_background(screen, self.world.speed)
        self.renderer.draw_obstacles(screen, self.world.obstacles)
        self.renderer.draw_medals(screen, self.world.medals)
        self.renderer.draw_player_blinking(screen, self.player)
        self.renderer.draw_ski_ui(
            screen, self.world.score, self.world.medal_score,
            self.player.lives, self.time_to_shooting
        )

        self.renderer.draw_floating_text(screen, self.floating_texts)
        if self.flash_alpha > 0:
            self.renderer.draw_flash(screen, self.flash_color, self.flash_alpha)

        # Countdown avant tir
        if self.pre_shooting_countdown:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            self.renderer.draw_countdown(screen, self.countdown_step)

        # Menu pause
        if self.paused:
            self._render_pause_menu(screen)

    def _render_pause_menu(self, screen):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.renderer.font_big.render("PAUSE", True, (255, 255, 255))
        screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, settings.HEIGHT // 2 - 200))

        labels = ["Reprendre", "Menu Principal", "Quitter"]
        mouse_pos = pygame.mouse.get_pos()

        for i, (btn, label) in enumerate(zip(self.pause_buttons, labels)):
            hovered = btn.collidepoint(mouse_pos) or i == self.pause_selected
            color = (80, 140, 200) if hovered else (50, 60, 80)
            border_color = (120, 180, 255) if hovered else (100, 110, 130)

            pygame.draw.rect(screen, color, btn, border_radius=12)
            pygame.draw.rect(screen, border_color, btn, 3, border_radius=12)

            text = self.renderer.font_medium.render(label, True, (255, 255, 255))
            screen.blit(text, (btn.centerx - text.get_width() // 2, btn.centery - text.get_height() // 2))

        hint = self.renderer.font_tiny.render("Fleches + Entree ou cliquez", True, (150, 150, 160))
        screen.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2, settings.HEIGHT // 2 + 180))


PlayScene = SkiScene
