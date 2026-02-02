import pygame

from game.controllers.input import InputController
from game.core import settings
from game.models.entities import Player
from game.models.world import World
from game.scenes.base import Scene
from game.views.renderer import Renderer


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()

    def handle_event(self, event):
        self.input.handle_event(event)

    def update(self, dt):
        left, right, jump, start = self.input.consume()
        if start or jump:
            self.game.change_scene(PlayScene(self.game))

    def render(self, screen):
        self.renderer.draw_background(screen)
        self.renderer.draw_title(screen, "Runner 2D", "Enter pour jouer | Esc pour quitter")


class PlayScene(Scene):
    def __init__(self, game, player=None, world=None, lives=None, shooting_timer_ms=0):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = player or Player()
        self.world = world or World()
        self.lives = settings.INITIAL_LIVES if lives is None else lives
        self.shooting_timer_ms = shooting_timer_ms

    def handle_event(self, event):
        self.input.handle_event(event)

    def update(self, dt):
        self.shooting_timer_ms += dt
        if self.shooting_timer_ms >= settings.SHOOTING_INTERVAL_MS:
            self.game.change_scene(ShootingScene(self.game, self.player, self.world, self.lives))
            return

        left, right, jump, _start = self.input.consume()
        if left:
            self.player.move_left()
        if right:
            self.player.move_right()
        if jump:
            self.player.jump()

        self.player.update(dt)
        self.world.update(dt)

        for obstacle in self.world.obstacles:
            if not obstacle.passed and obstacle.y > self.player.y:
                obstacle.passed = True
                self.world.score += 1

        if self.check_collisions():
            if self.lives > 0:
                self.lives -= 1
                self.world.obstacles = []
                self.player.lane = 1
                self.player.y = settings.PLAYER_Y
                self.player.velocity_y = 0.0
                self.player.on_ground = True
            else:
                self.game.change_scene(GameOverScene(self.game, self.world.score))

    def check_collisions(self):
        px, py, pw, ph = self.player.rect
        for obstacle in self.world.obstacles:
            ox, oy, ow, oh = obstacle.rect
            if px < ox + ow and px + pw > ox and py < oy + oh and py + ph > oy:
                return True
        return False

    def render(self, screen):
        self.renderer.draw_background(screen)
        self.renderer.draw_obstacles(screen, self.world.obstacles)
        self.renderer.draw_player(screen, self.player)
        self.renderer.draw_ui(screen, self.world.score, self.world.speed, self.lives)
        self.renderer.draw_lane_marker(screen, self.player.lane)


class ShootingScene(Scene):
    def __init__(self, game, player, world, lives):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = player
        self.world = world
        self.lives = lives

        self.targets_hit = [False for _ in range(settings.SHOOTING_TARGET_COUNT)]
        self.shots_taken = 0
        self.time_left_ms = settings.SHOOTING_DURATION_MS

        self.target_positions = self._build_target_positions()
        self.cursor_x = float(settings.SHOOTING_MARGIN_X)
        self.cursor_dir = 1.0

    def _build_target_positions(self):
        count = settings.SHOOTING_TARGET_COUNT
        if count <= 1:
            return [settings.WIDTH // 2]

        margin = settings.SHOOTING_MARGIN_X
        span = settings.WIDTH - 2 * margin
        step = span / (count - 1)
        return [int(margin + i * step) for i in range(count)]

    def handle_event(self, event):
        self.input.handle_event(event)

    def update(self, dt):
        _left, _right, shoot, _start = self.input.consume()

        self.time_left_ms -= dt
        if self.time_left_ms <= 0:
            if all(self.targets_hit):
                self.lives += 1
            self.game.change_scene(
                PlayScene(
                    self.game,
                    player=self.player,
                    world=self.world,
                    lives=self.lives,
                    shooting_timer_ms=0,
                )
            )
            return

        dt_s = dt * 0.001
        self.cursor_x += self.cursor_dir * settings.SHOOTING_CURSOR_SPEED * dt_s

        min_x = float(settings.SHOOTING_MARGIN_X)
        max_x = float(settings.WIDTH - settings.SHOOTING_MARGIN_X)
        if self.cursor_x <= min_x:
            self.cursor_x = min_x
            self.cursor_dir = 1.0
        elif self.cursor_x >= max_x:
            self.cursor_x = max_x
            self.cursor_dir = -1.0

        if shoot and self.shots_taken < settings.SHOOTING_BULLETS:
            self.shots_taken += 1
            for i, x in enumerate(self.target_positions):
                if self.targets_hit[i]:
                    continue
                if abs(self.cursor_x - x) <= settings.SHOOTING_TARGET_RADIUS:
                    self.targets_hit[i] = True
                    break

            if all(self.targets_hit):
                self.lives += 1
                self.game.change_scene(
                    PlayScene(
                        self.game,
                        player=self.player,
                        world=self.world,
                        lives=self.lives,
                        shooting_timer_ms=0,
                    )
                )
                return

            if self.shots_taken >= settings.SHOOTING_BULLETS:
                if all(self.targets_hit):
                    self.lives += 1
                self.game.change_scene(
                    PlayScene(
                        self.game,
                        player=self.player,
                        world=self.world,
                        lives=self.lives,
                        shooting_timer_ms=0,
                    )
                )

    def render(self, screen):
        shots_left = settings.SHOOTING_BULLETS - self.shots_taken
        time_left_s = max(0, int(self.time_left_ms // 1000))
        self.renderer.draw_shooting(
            screen,
            self.target_positions,
            self.targets_hit,
            int(self.cursor_x),
            shots_left,
            time_left_s,
            self.lives,
        )


class GameOverScene(Scene):
    def __init__(self, game, score):
        super().__init__(game)
        self.score = score
        self.input = InputController()
        self.renderer = Renderer()

    def handle_event(self, event):
        self.input.handle_event(event)

    def update(self, dt):
        left, right, jump, start = self.input.consume()
        if start or jump:
            self.game.change_scene(PlayScene(self.game))

    def render(self, screen):
        self.renderer.draw_background(screen)
        self.renderer.draw_title(screen, "Game Over", f"Score: {self.score} | Enter pour rejouer")
