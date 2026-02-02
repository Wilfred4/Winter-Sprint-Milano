import pygame

from game.core import settings

from game.controllers.input import InputController
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
    def __init__(self, game):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = Player()
        self.world = World()

    def handle_event(self, event):
        self.input.handle_event(event)

    def update(self, dt):
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

        self.handle_medal_pickups()

        if self.check_collisions():
            self.game.change_scene(GameOverScene(self.game, self.world.score))

    def check_collisions(self):
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
            else:
                remaining.append(medal)
        self.world.medals = remaining

    def render(self, screen):
        self.renderer.draw_background(screen)
        self.renderer.draw_obstacles(screen, self.world.obstacles)
        self.renderer.draw_medals(screen, self.world.medals)
        self.renderer.draw_player(screen, self.player)
        self.renderer.draw_ui(screen, self.world.score, self.world.medal_score, self.world.speed)
        self.renderer.draw_lane_marker(screen, self.player.lane)


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
