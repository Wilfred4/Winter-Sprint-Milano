import pygame

from game.core import settings
from game.controllers.input import InputController
from game.scenes.base import Scene
from game.views.renderer import Renderer
from game.scenes.audio import MusicManager, SoundManager


class MenuScene(Scene):
    """Menu principal du jeu."""

    def __init__(self, game):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        MusicManager.play_menu_music()

        # Taille des boutons (configurable dans settings.py)
        btn_width = settings.MENU_BUTTON_WIDTH
        btn_height = settings.MENU_BUTTON_HEIGHT
        self.biathlon_button = pygame.Rect(0, 0, btn_width, btn_height)
        self.hockey_button = pygame.Rect(0, 0, btn_width, btn_height)
        self.leaderboard_button = pygame.Rect(0, 0, btn_width, btn_height)
        self.settings_button = pygame.Rect(0, 0, btn_width, btn_height)
        self.quit_button = pygame.Rect(0, 0, btn_width, btn_height)

        # Positionnement des boutons (empilés vers le bas de l'écran)
        center_x = settings.WIDTH // 2
        spacing = settings.MENU_BUTTON_SPACING
        bottom_margin = settings.MENU_BUTTON_BOTTOM_MARGIN
        self.quit_button.center = (center_x, settings.HEIGHT - bottom_margin - btn_height // 2)
        self.settings_button.center = (center_x, self.quit_button.centery - btn_height - spacing)
        self.leaderboard_button.center = (center_x, self.settings_button.centery - btn_height - spacing)
        self.hockey_button.center = (center_x, self.leaderboard_button.centery - btn_height - spacing)
        self.biathlon_button.center = (center_x, self.hockey_button.centery - btn_height - spacing)

    def handle_event(self, event):
        self.input.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        from game.hockey.scene import HockeyScene
        from game.scenes.leaderboard import LeaderboardScene

        if self.biathlon_button.collidepoint(pos):
            self._start_biathlon()
        elif self.hockey_button.collidepoint(pos):
            self.game.change_scene(HockeyScene(self.game))
        elif self.leaderboard_button.collidepoint(pos):
            self.game.change_scene(LeaderboardScene(self.game))
        elif self.settings_button.collidepoint(pos):
            pass  # TODO
        elif self.quit_button.collidepoint(pos):
            self.game.running = False

    def _start_biathlon(self):
        from game.scenes.countdown import CountdownScene

        Renderer.reset_background_index()
        MusicManager.play_game_music()
        SoundManager.init()
        self.game.change_scene(CountdownScene(self.game, with_start=True))

    def update(self, dt):
        left, right, jump, start = self.input.consume()
        if start or jump:
            self._start_biathlon()

    def render(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        # Liste des boutons dans l'ordre d'affichage (du haut vers le bas)
        button_list = [
            (self.biathlon_button, "BIATHLON"),
            (self.hockey_button, "HOCKEY"),
            (self.leaderboard_button, "LEADERBOARD"),
            (self.settings_button, "SETTINGS"),
            (self.quit_button, "QUITTER"),
        ]
        # Un seul bouton peut être surligné (le premier touché)
        hovered_index = -1
        for i, (rect, _) in enumerate(button_list):
            if rect.collidepoint(mouse_pos):
                hovered_index = i
                break
        buttons = [
            (rect, i == hovered_index, label)
            for i, (rect, label) in enumerate(button_list)
        ]
        self.renderer.draw_menu(screen, buttons)
