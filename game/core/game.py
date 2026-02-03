import pygame

from game.core import settings
from game.scenes.runner import MenuScene


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Runner 2D")
        self.fullscreen = settings.FULLSCREEN
        self.screen = self._set_display()
        self.clock = pygame.time.Clock()
        self.scene = MenuScene(self)
        self.running = True

    def change_scene(self, scene):
        self.scene = scene

    def _set_display(self):
        flags = pygame.SCALED
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        return pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), flags)

    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    self.screen = self._set_display()
                self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.render(self.screen)
            pygame.display.flip()

        pygame.quit()
