import pygame

from game.core import settings
from game.scenes.base import Scene
from game.views.renderer import Renderer


class CountdownScene(Scene):
    """Compte à rebours avant le début de la partie (3, 2, 1, GO)."""

    def __init__(self, game, with_start=False, next_scene_callback=None, player=None, world=None):
        super().__init__(game)
        self.renderer = Renderer()
        self.with_start = with_start
        self.next_scene_callback = next_scene_callback
        self.player = player
        self.world = world

        # Etapes du countdown
        self.steps = [3, 2, 1]
        if with_start:
            self.steps.append("start")

        self.current_step = 0
        self.step_timer = 0

    def handle_event(self, event):
        pass  # Pas d'input pendant le countdown

    def update(self, dt):
        self.step_timer += dt

        if self.step_timer >= settings.COUNTDOWN_STEP_DURATION:
            self.step_timer = 0
            self.current_step += 1

            if self.current_step >= len(self.steps):
                # Countdown terminé, on passe à la suite
                if self.next_scene_callback:
                    self.next_scene_callback()
                else:
                    from game.scenes.ski import SkiScene
                    self.game.change_scene(SkiScene(self.game))

    def render(self, screen):
        self.renderer.draw_background(screen, 0)

        # Overlay sombre
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            # Progress de 0.0 à 1.0 dans l'étape actuelle
            progress = self.step_timer / settings.COUNTDOWN_STEP_DURATION
            self.renderer.draw_countdown(screen, step, progress)
