import pygame

from game.core import settings
from game.controllers.input import InputController
from game.scenes.base import Scene
from game.views.renderer import Renderer


class LeaderboardScene(Scene):
    """Affiche le classement des meilleurs scores."""

    def __init__(self, game):
        super().__init__(game)
        self.renderer = Renderer()
        self.input = InputController()
        self.scores = []
        self.loading = True
        self.error = False
        self.error_message = None
        self._load_scores()

    def _load_scores(self):
        try:
            from game.backend.supabase_client import recuperer_high_scores
            self.scores = recuperer_high_scores(10)
            self.loading = False
        except Exception as e:
            print(f"Erreur chargement leaderboard: {e}")
            self.loading = False
            self.error = True
            self.error_message = str(e)

    def handle_event(self, event):
        self.input.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_m, pygame.K_RETURN):
                from game.scenes.menu import MenuScene
                self.game.change_scene(MenuScene(self.game))

    def update(self, dt):
        pass

    def render(self, screen):
        # Fond
        if self.renderer.menu_image:
            screen.blit(self.renderer.menu_image, (0, 0))
        else:
            screen.fill(settings.BG_COLOR)

        # Overlay sombre
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Panel central
        panel_w, panel_h = 700, 650
        panel_x = settings.WIDTH // 2 - panel_w // 2
        panel_y = settings.HEIGHT // 2 - panel_h // 2
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)

        # Fond du panel avec dégradé
        for y in range(panel_h):
            alpha = 200 - int(y * 0.1)
            pygame.draw.line(panel, (20, 30, 50, alpha), (0, y), (panel_w, y))

        # Bordure
        pygame.draw.rect(panel, (100, 140, 200, 150), (0, 0, panel_w, panel_h), 3, border_radius=20)
        screen.blit(panel, (panel_x, panel_y))

        # Titre
        title = self.renderer.font_big.render("LEADERBOARD", True, (255, 215, 0))
        screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, panel_y + 30))

        # Ligne décorative
        pygame.draw.line(screen, (100, 140, 200),
                        (panel_x + 50, panel_y + 100),
                        (panel_x + panel_w - 50, panel_y + 100), 2)

        if self.loading:
            # Animation de chargement
            loading = self.renderer.font_medium.render("Chargement...", True, (200, 200, 200))
            screen.blit(loading, (settings.WIDTH // 2 - loading.get_width() // 2,
                                  settings.HEIGHT // 2 - loading.get_height() // 2))

        elif self.error:
            # Message d'erreur
            error = self.renderer.font_small.render("Erreur de connexion", True, (255, 100, 100))
            screen.blit(error, (settings.WIDTH // 2 - error.get_width() // 2,
                               settings.HEIGHT // 2 - 20))
            hint = self.renderer.font_tiny.render("Vérifiez votre connexion internet", True, (180, 180, 180))
            screen.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2,
                              settings.HEIGHT // 2 + 20))

        else:
            # Afficher les scores
            y_offset = panel_y + 130

            if not self.scores:
                empty = self.renderer.font_small.render("Aucun score enregistré", True, (180, 180, 180))
                screen.blit(empty, (settings.WIDTH // 2 - empty.get_width() // 2, y_offset + 50))
            else:
                for i, score_data in enumerate(self.scores):
                    username = score_data.get('name', 'Anonyme')[:15]
                    score = score_data.get('score', 0)

                    # Couleur selon le rang
                    if i == 0:
                        color = (255, 215, 0)  # Or
                        rank_icon = "🥇"
                    elif i == 1:
                        color = (200, 200, 210)  # Argent
                        rank_icon = "🥈"
                    elif i == 2:
                        color = (205, 127, 50)  # Bronze
                        rank_icon = "🥉"
                    else:
                        color = (220, 220, 230)
                        rank_icon = f"{i + 1}."

                    # Rang
                    rank_text = self.renderer.font_small.render(rank_icon, True, color)
                    screen.blit(rank_text, (panel_x + 80, y_offset))

                    # Nom
                    name_text = self.renderer.font_small.render(username, True, color)
                    screen.blit(name_text, (panel_x + 150, y_offset))

                    # Score
                    score_text = self.renderer.font_small.render(f"{score:,}".replace(",", " "), True, color)
                    screen.blit(score_text, (panel_x + panel_w - 150 - score_text.get_width(), y_offset))

                    y_offset += 48

        # Instructions
        instr = self.renderer.font_tiny.render("ECHAP / M / ENTER pour revenir au menu", True, (150, 150, 160))
        screen.blit(instr, (settings.WIDTH // 2 - instr.get_width() // 2, panel_y + panel_h - 40))


class PseudoInputScene(Scene):
    """Demande le pseudo du joueur pour sauvegarder le score."""

    def __init__(self, game, score, medal_score, distance):
        super().__init__(game)
        self.score = score
        self.medal_score = medal_score
        self.distance = distance
        self.renderer = Renderer()
        self.text_input = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_length = 15
        self.error_message = None
        self.saving = False

    def handle_event(self, event):
        if self.saving:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                pseudo = self.text_input.strip() or "Anonyme"
                self._save_score(pseudo)

            elif event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
                self.error_message = None

            elif event.key == pygame.K_ESCAPE:
                self._return_to_menu()

            else:
                if len(self.text_input) < self.max_length and event.unicode.isprintable():
                    self.text_input += event.unicode
                    self.error_message = None

    def _save_score(self, pseudo):
        self.saving = True
        try:
            from game.backend.supabase_client import sauvegarder_score
            sauvegarder_score(pseudo, self.score)
            self._return_to_menu()
        except Exception as e:
            self.error_message = "Erreur de sauvegarde"
            self.saving = False
            print(f"Erreur sauvegarde score: {e}")

    def _return_to_menu(self):
        from game.scenes.menu import MenuScene
        from game.scenes.audio import MusicManager
        MusicManager.play_menu_music()
        self.game.change_scene(MenuScene(self.game))

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def render(self, screen):
        # Fond
        self.renderer.draw_background(screen, 0)

        # Overlay
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        cx, cy = settings.WIDTH // 2, settings.HEIGHT // 2

        # Panel
        panel_w, panel_h = 600, 400
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for y in range(panel_h):
            alpha = 200 - int(y * 0.15)
            pygame.draw.line(panel, (20, 30, 50, alpha), (0, y), (panel_w, y))
        pygame.draw.rect(panel, (100, 140, 200, 150), (0, 0, panel_w, panel_h), 3, border_radius=20)
        screen.blit(panel, (cx - panel_w // 2, cy - panel_h // 2))

        # Titre
        title = self.renderer.font_big.render("NOUVEAU SCORE !", True, (255, 215, 0))
        screen.blit(title, (cx - title.get_width() // 2, cy - 160))

        # Score
        score_text = self.renderer.font_medium.render(f"{self.score:,}".replace(",", " "), True, (255, 255, 255))
        screen.blit(score_text, (cx - score_text.get_width() // 2, cy - 100))

        # Label
        label = self.renderer.font_small.render("Entrez votre pseudo :", True, (200, 200, 210))
        screen.blit(label, (cx - label.get_width() // 2, cy - 30))

        # Zone de saisie
        input_w, input_h = 400, 50
        input_rect = pygame.Rect(cx - input_w // 2, cy + 10, input_w, input_h)
        pygame.draw.rect(screen, (30, 40, 60), input_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 140, 200), input_rect, 2, border_radius=8)

        # Texte saisi
        cursor = "|" if self.cursor_visible else ""
        display_text = self.text_input + cursor
        input_text = self.renderer.font_medium.render(display_text, True, (255, 255, 255))
        screen.blit(input_text, (input_rect.x + 15, input_rect.y + 8))

        # Message d'erreur
        if self.error_message:
            error = self.renderer.font_small.render(self.error_message, True, (255, 100, 100))
            screen.blit(error, (cx - error.get_width() // 2, cy + 80))

        # Message de sauvegarde
        if self.saving:
            saving = self.renderer.font_small.render("Sauvegarde...", True, (100, 200, 100))
            screen.blit(saving, (cx - saving.get_width() // 2, cy + 80))

        # Instructions
        instr = self.renderer.font_tiny.render("ENTER pour sauvegarder  •  ECHAP pour annuler", True, (150, 150, 160))
        screen.blit(instr, (cx - instr.get_width() // 2, cy + 140))
