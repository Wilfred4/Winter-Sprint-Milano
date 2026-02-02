import pygame

from game.core import settings
from game.scenes.runner import MenuScene


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Runner 2D")
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()
        self.scene = MenuScene(self)
        self.running = True

    def change_scene(self, scene):
        self.scene = scene

    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.render(self.screen)
            pygame.display.flip()

        pygame.quit()
