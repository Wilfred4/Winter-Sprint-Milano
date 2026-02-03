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
        self.start_button = pygame.Rect(0, 0, 300, 84)
        self.quit_button = pygame.Rect(0, 0, 300, 84)
        self.start_button.center = (settings.WIDTH // 2, settings.HEIGHT - 180)
        self.quit_button.center = (settings.WIDTH // 2, settings.HEIGHT - 100)

    def handle_event(self, event):
        self.input.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.collidepoint(event.pos):
                self.game.change_scene(PlayScene(self.game))
            if self.quit_button.collidepoint(event.pos):
                self.game.running = False

    def update(self, dt):
        left, right, jump, start = self.input.consume()
        if start or jump:
            self.game.change_scene(PlayScene(self.game))

    def render(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        start_hovered = self.start_button.collidepoint(mouse_pos)
        quit_hovered = self.quit_button.collidepoint(mouse_pos)
        self.renderer.draw_menu(screen, self.start_button, start_hovered, self.quit_button, quit_hovered)


class PlayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = Player()
        self.world = World()
        self.paused = False

    def handle_event(self, event):
        self.input.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused

    def update(self, dt):
        if self.paused:
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
        self.renderer.draw_background(screen, self.world.speed)
        self.renderer.draw_obstacles(screen, self.world.obstacles)
        self.renderer.draw_medals(screen, self.world.medals)
        self.renderer.draw_player(screen, self.player)
        self.renderer.draw_ui(screen, self.world.score, self.world.medal_score, self.world.speed)
        self.renderer.draw_lane_marker(screen, self.player.lane)
        if self.paused:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            self.renderer.draw_title(screen, "Pause", "Echap pour reprendre")


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
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        self.renderer.draw_title(screen, "Game Over", f"Score: {self.score} | Enter pour rejouer")
