import pygame

from game.core import settings
from game.controllers.input import InputController
from game.scenes.base import Scene
from game.views.renderer import Renderer
from game.scenes.audio import MusicManager


class GameOverScene(Scene):
    """Ecran de fin de partie."""

    def __init__(self, game, score, medal_score=0, distance=0):
        super().__init__(game)
        self.score = score
        self.medal_score = medal_score
        self.distance = distance
        self.input = InputController()
        self.renderer = Renderer()
        self.animation_time = 0
        self.can_restart = False

        # Charger et sauvegarder le meilleur score
        self.best_score = self._load_best_score()
        if score > self.best_score:
            self._save_best_score(score)
            self.best_score = score

    def _load_best_score(self):
        score_file = settings.ASSETS_DIR / "best_score.txt"
        try:
            if score_file.exists():
                content = score_file.read_text().strip()
                return int(content) if content else 0
        except (ValueError, IOError):
            pass
        return 0

    def _save_best_score(self, score):
        score_file = settings.ASSETS_DIR / "best_score.txt"
        try:
            score_file.write_text(str(score))
        except IOError:
            pass  # Pas grave si ça marche pas

    def handle_event(self, event):
        self.input.handle_event(event)

        if event.type == pygame.KEYDOWN and self.can_restart:
            if event.key == pygame.K_m:
                from game.scenes.menu import MenuScene
                MusicManager.play_menu_music()
                self.game.change_scene(MenuScene(self.game))

    def update(self, dt):
        self.animation_time += dt / 1000

        if self.animation_time >= 1.5:
            self.can_restart = True

        _, _, jump, start = self.input.consume()
        if self.can_restart and (start or jump):
            from game.scenes.countdown import CountdownScene
            Renderer.reset_background_index()
            MusicManager.play_game_music()
            self.game.change_scene(CountdownScene(self.game, with_start=True))

    def render(self, screen):
        self.renderer.draw_background(screen)
        progress = min(1.0, self.animation_time / 1.5)
        self.renderer.draw_game_over(
            screen, self.score, self.medal_score,
            self.distance, self.best_score, progress
        )
