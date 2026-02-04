import pygame

from game.core import settings
from game.controllers.input import InputController
from game.models.entities import Player, Target, Sight, TargetState
from game.models.world import World
from game.scenes.base import Scene
from game.views.renderer import Renderer


# === GESTION DE LA MUSIQUE ===
class MusicManager:
    _current_music = None

    @classmethod
    def play_menu_music(cls):
        if cls._current_music != "menu":
            pygame.mixer.music.stop()
            if settings.MUSIC_MENU.exists():
                pygame.mixer.music.load(str(settings.MUSIC_MENU))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)  # -1 = boucle infinie
                cls._current_music = "menu"

    @classmethod
    def play_game_music(cls):
        if cls._current_music != "game":
            pygame.mixer.music.stop()
            if settings.MUSIC_GAME.exists():
                pygame.mixer.music.load(str(settings.MUSIC_GAME))
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)  # -1 = boucle infinie
                cls._current_music = "game"

    @classmethod
    def stop(cls):
        pygame.mixer.music.stop()
        cls._current_music = None


# === GESTION DES SONS ===
class SoundManager:
    _coin_sound = None

    @classmethod
    def init(cls):
        # Charger le son de pièce s'il existe
        if settings.SOUND_COIN.exists():
            cls._coin_sound = pygame.mixer.Sound(str(settings.SOUND_COIN))
            cls._coin_sound.set_volume(0.6)
        else:
            # Essayer .wav
            coin_wav = settings.ASSETS_DIR / "coin.wav"
            if coin_wav.exists():
                cls._coin_sound = pygame.mixer.Sound(str(coin_wav))
                cls._coin_sound.set_volume(0.6)

    @classmethod
    def play_coin(cls):
        if cls._coin_sound:
            cls._coin_sound.play()


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()

        # Lancer la musique du menu
        MusicManager.play_menu_music()

        # 3 boutons : Biathlon, Hockey, Quitter
        # Ratio des images: 1344x768 = 1.75
        btn_width, btn_height = 280, 140
        self.biathlon_button = pygame.Rect(0, 0, btn_width, btn_height)
        self.hockey_button = pygame.Rect(0, 0, btn_width, btn_height)
        self.quit_button = pygame.Rect(0, 0, btn_width, btn_height)

        # Positions resserrées vers le bas pour voir le logo
        center_x = settings.WIDTH // 2
        spacing = 10  # Espacement entre boutons
        bottom_margin = 50  # Marge depuis le bas
        self.quit_button.center = (center_x, settings.HEIGHT - bottom_margin - btn_height // 2)
        self.hockey_button.center = (center_x, self.quit_button.centery - btn_height - spacing)
        self.biathlon_button.center = (center_x, self.hockey_button.centery - btn_height - spacing)

    def handle_event(self, event):
        self.input.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.biathlon_button.collidepoint(event.pos):
                Renderer.reset_background_index()
                MusicManager.play_game_music()
                SoundManager.init()
                self.game.change_scene(CountdownScene(self.game, with_start=True))
            if self.hockey_button.collidepoint(event.pos):
                # TODO: Lancer le mode Hockey quand il sera implémenté
                pass
            if self.quit_button.collidepoint(event.pos):
                self.game.running = False

    def update(self, dt):
        left, right, jump, start = self.input.consume()
        if start or jump:
            Renderer.reset_background_index()
            MusicManager.play_game_music()
            SoundManager.init()
            self.game.change_scene(CountdownScene(self.game, with_start=True))

    def render(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        buttons = [
            (self.biathlon_button, self.biathlon_button.collidepoint(mouse_pos), "BIATHLON"),
            (self.hockey_button, self.hockey_button.collidepoint(mouse_pos), "HOCKEY"),
            (self.quit_button, self.quit_button.collidepoint(mouse_pos), "QUITTER"),
        ]
        self.renderer.draw_menu(screen, buttons)


class CountdownScene(Scene):
    """Scène de décompte 3, 2, 1 (et Start optionnel)"""

    def __init__(self, game, with_start=False, next_scene_callback=None, player=None, world=None):
        super().__init__(game)
        self.renderer = Renderer()
        self.with_start = with_start
        self.next_scene_callback = next_scene_callback
        self.player = player
        self.world = world

        # Séquence : 3, 2, 1, (start)
        self.steps = [3, 2, 1]
        if with_start:
            self.steps.append("start")

        self.current_step = 0
        self.step_timer = 0

    def handle_event(self, event):
        pass

    def update(self, dt):
        self.step_timer += dt

        if self.step_timer >= settings.COUNTDOWN_STEP_DURATION:
            self.step_timer = 0
            self.current_step += 1

            if self.current_step >= len(self.steps):
                # Décompte terminé
                if self.next_scene_callback:
                    self.next_scene_callback()
                else:
                    # Par défaut : lancer le jeu
                    self.game.change_scene(SkiScene(self.game))

    def render(self, screen):
        # Fond
        self.renderer.draw_background(screen, 0)

        # Overlay semi-transparent
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        # Afficher le chiffre/texte actuel
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.renderer.draw_countdown(screen, step)


class SkiScene(Scene):
    """Phase SKI - Course d'esquive"""

    def __init__(self, game, player=None, world=None, from_shooting=False):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = player if player else Player()
        self.world = world if world else World()
        self.paused = False
        self.time_to_shooting = settings.SHOOTING_INTERVAL

        # Si on revient du tir, délai avant que les obstacles réapparaissent
        self.from_shooting = from_shooting
        self.obstacle_spawn_delay = settings.OBSTACLE_SPAWN_DELAY if from_shooting else 0

        # Supprimer tous les obstacles quand on revient du tir
        if from_shooting:
            self.world.obstacles.clear()

        # État de préparation avant le tir (suppression des obstacles)
        self.pre_shooting_preparation = False
        self.preparation_timer = 0

        # État du décompte avant le tir
        self.pre_shooting_countdown = False
        self.countdown_step = 3
        self.countdown_timer = 0

        # Effets visuels
        self.flash_color = None
        self.flash_alpha = 0
        self.floating_texts = []

        # Menu pause
        self.pause_selected = 0  # 0=Reprendre, 1=Menu, 2=Quitter
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
        if action == 0:  # Reprendre
            self.paused = False
        elif action == 1:  # Menu principal
            Renderer.reset_background_index()
            MusicManager.play_menu_music()
            self.game.change_scene(MenuScene(self.game))
        elif action == 2:  # Quitter
            self.game.running = False

    def update(self, dt):
        if self.paused:
            return

        left, right, jump, _start = self.input.consume()

        # Gérer la phase de préparation (suppression des obstacles)
        if self.pre_shooting_preparation:
            self._update_pre_shooting_preparation(dt, left, right, jump)
            return

        # Gérer le décompte avant le tir (joueur peut bouger)
        if self.pre_shooting_countdown:
            self._update_pre_shooting_countdown(dt, left, right, jump)
            return

        if left:
            self.player.move_left()
        if right:
            self.player.move_right()
        if jump:
            self.player.jump()

        self.player.update(dt)

        # Mise à jour du délai de spawn après le tir
        if self.obstacle_spawn_delay > 0:
            self.obstacle_spawn_delay -= dt
            # Mettre à jour le monde mais sans spawn d'obstacles
            self.world.distance += dt * 0.001
            # Utiliser la même formule que world.update()
            self.world.speed = min(
                settings.MAX_SCROLL_SPEED,
                settings.BASE_SCROLL_SPEED + self.world.distance * settings.SPEED_GROWTH
            )
            # Déplacer les obstacles existants
            for obstacle in self.world.obstacles:
                obstacle.update(self.world.speed)
            for medal in self.world.medals:
                medal.update(self.world.speed)
            self.world.obstacles = [o for o in self.world.obstacles if o.y - o.height < settings.HEIGHT + 40]
            self.world.medals = [m for m in self.world.medals if m.y - m.height < settings.HEIGHT + 40]
        else:
            self.world.update(dt)

        # Mise à jour des effets visuels
        self._update_effects(dt)

        # Timer pour la phase de tir
        self.time_to_shooting -= dt
        if self.time_to_shooting <= 0:
            # Lancer la phase de préparation (suppression des obstacles)
            self.pre_shooting_preparation = True
            self.preparation_timer = 0
            # Supprimer tous les obstacles immédiatement
            self.world.obstacles.clear()
            return

        # Score basé sur les obstacles évités
        for obstacle in self.world.obstacles:
            if not obstacle.passed and obstacle.y > self.player.y:
                obstacle.passed = True
                self.world.score += 1

        # Ramasser les médailles
        self.handle_medal_pickups()

        # Vérifier les collisions
        if self.check_collisions():
            self._trigger_flash((255, 0, 0), 150)
            if self.player.take_damage():
                self.game.change_scene(GameOverScene(self.game, self.world.score, self.world.medal_score, self.world.distance))

    def _update_pre_shooting_preparation(self, dt, left, right, jump):
        """Phase de préparation avant le décompte - pas d'obstacles, joueur peut bouger"""
        self.preparation_timer += dt

        # Le joueur peut toujours bouger
        if left:
            self.player.move_left()
        if right:
            self.player.move_right()
        if jump:
            self.player.jump()
        self.player.update(dt)

        # Continuer le scroll mais sans obstacles
        self.world.distance += dt * 0.001
        self.world.speed = min(
            settings.MAX_SCROLL_SPEED,
            settings.BASE_SCROLL_SPEED + self.world.distance * settings.SPEED_GROWTH
        )

        # Déplacer les médailles restantes
        for medal in self.world.medals:
            medal.update(self.world.speed)
        self.world.medals = [m for m in self.world.medals if m.y - m.height < settings.HEIGHT + 40]

        # Ramasser les médailles pendant la préparation
        self.handle_medal_pickups()

        # Mise à jour des effets
        self._update_effects(dt)

        # Après le temps de préparation, lancer le décompte
        if self.preparation_timer >= settings.PRE_SHOOTING_CLEAR_TIME:
            self.pre_shooting_preparation = False
            self.pre_shooting_countdown = True
            self.countdown_step = 3
            self.countdown_timer = 0

    def _update_pre_shooting_countdown(self, dt, left, right, jump):
        """Met à jour le décompte avant la phase de tir - joueur peut bouger"""
        self.countdown_timer += dt

        # Le joueur peut toujours bouger pendant le décompte
        if left:
            self.player.move_left()
        if right:
            self.player.move_right()
        if jump:
            self.player.jump()
        self.player.update(dt)

        # Continuer le scroll mais sans obstacles
        self.world.distance += dt * 0.001
        for medal in self.world.medals:
            medal.update(self.world.speed)
        self.world.medals = [m for m in self.world.medals if m.y - m.height < settings.HEIGHT + 40]

        # Ramasser les médailles pendant le décompte
        self.handle_medal_pickups()

        # Mise à jour des effets
        self._update_effects(dt)

        if self.countdown_timer >= settings.COUNTDOWN_STEP_DURATION:
            self.countdown_timer = 0
            self.countdown_step -= 1

            if self.countdown_step <= 0:
                # Décompte terminé, passer à la phase de tir
                self.game.change_scene(ShootingScene(self.game, self.player, self.world))

    def _update_effects(self, dt):
        if self.flash_alpha > 0:
            self.flash_alpha -= dt * 0.3
            if self.flash_alpha < 0:
                self.flash_alpha = 0

        for t in self.floating_texts:
            t['y'] -= dt * 0.05
            t['alpha'] -= dt * 0.15
        self.floating_texts = [t for t in self.floating_texts if t['alpha'] > 0]

    def _trigger_flash(self, color, alpha):
        self.flash_color = color
        self.flash_alpha = alpha

    def _add_floating_text(self, text, x, y, color):
        self.floating_texts.append({
            'text': text,
            'x': x,
            'y': y,
            'color': color,
            'alpha': 255,
            'scale': 1.0
        })

    def check_collisions(self):
        if self.player.is_invincible():
            return False

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
                color = (255, 215, 0) if medal.kind == "gold" else (200, 200, 200) if medal.kind == "silver" else (205, 127, 50)
                self._add_floating_text(f"+{points}", mx + mw // 2, my, color)
                SoundManager.play_coin()  # Jouer le son de pièce
            else:
                remaining.append(medal)
        self.world.medals = remaining

    def render(self, screen):
        self.renderer.draw_background(screen, self.world.speed)
        self.renderer.draw_obstacles(screen, self.world.obstacles)
        self.renderer.draw_medals(screen, self.world.medals)
        self.renderer.draw_player_blinking(screen, self.player)
        self.renderer.draw_ski_ui(screen, self.world.score, self.world.medal_score, self.player.lives, self.time_to_shooting)

        # Effets visuels
        self.renderer.draw_floating_text(screen, self.floating_texts)
        if self.flash_alpha > 0:
            self.renderer.draw_flash(screen, self.flash_color, self.flash_alpha)

        # Décompte avant le tir
        if self.pre_shooting_countdown:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            self.renderer.draw_countdown(screen, self.countdown_step)

        if self.paused:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            # Titre PAUSE
            title = self.renderer.font_big.render("PAUSE", True, (255, 255, 255))
            screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, settings.HEIGHT // 2 - 200))

            # Boutons du menu pause
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

            # Instruction
            hint = self.renderer.font_tiny.render("Flèches + Entrée ou cliquez", True, (150, 150, 160))
            screen.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2, settings.HEIGHT // 2 + 180))


class ShootingScene(Scene):
    """Phase TIR - Mini-jeu de précision"""

    def __init__(self, game, player, world):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = player
        self.world = world

        # Créer les 5 cibles (positionnées dans la bannière)
        self.targets = []
        margin = 200  # Marge sur les côtés
        total_width = settings.WIDTH - 2 * margin
        spacing = total_width // (settings.NUM_TARGETS - 1)
        for i in range(settings.NUM_TARGETS):
            x = margin + i * spacing - settings.TARGET_SIZE[0] // 2
            self.targets.append(Target(x=x))

        # Créer le viseur (au même niveau Y que les cibles)
        self.sight = Sight()

        self.current_target_index = 0
        self.shots_remaining = settings.NUM_TARGETS
        self.targets_hit = 0
        self.shot_cooldown = 0
        self.transition_timer = 0
        self.phase_complete = False

        # Effets visuels
        self.floating_texts = []
        self.flash_color = None
        self.flash_alpha = 0

        # Animation de recul de l'arme
        self.gun_recoil = 0  # Offset vertical pour le recul
        self.gun_recoil_speed = 0

        # Son de tir
        self.shotgun_sound = None
        if settings.SOUND_SHOTGUN.exists():
            self.shotgun_sound = pygame.mixer.Sound(str(settings.SOUND_SHOTGUN))
            self.shotgun_sound.set_volume(0.5)

    def handle_event(self, event):
        self.input.handle_event(event)

    def update(self, dt):
        left, right, jump, _start = self.input.consume()

        self._update_effects(dt)

        if self.shot_cooldown > 0:
            self.shot_cooldown -= dt

        if self.phase_complete:
            self.transition_timer += dt
            if self.transition_timer >= 1500:
                if self.targets_hit == settings.NUM_TARGETS:
                    self.player.lives += 1
                elif self.targets_hit < settings.MIN_TARGETS_TO_HIT:
                    if self.player.take_damage():
                        self.game.change_scene(GameOverScene(self.game, self.world.score, self.world.medal_score, self.world.distance))
                        return
                # Changer de map après la phase de tir
                self.renderer.next_background()
                # Retourner au ski avec délai d'obstacles
                self.game.change_scene(SkiScene(self.game, self.player, self.world, from_shooting=True))
            return

        self.sight.update()

        if jump and self.shot_cooldown <= 0 and self.current_target_index < len(self.targets):
            self.shoot()
            self.shot_cooldown = 400

    def _update_effects(self, dt):
        if self.flash_alpha > 0:
            self.flash_alpha -= dt * 0.3
        for t in self.floating_texts:
            t['y'] -= dt * 0.05
            t['alpha'] -= dt * 0.15
        self.floating_texts = [t for t in self.floating_texts if t['alpha'] > 0]

        # Animation de recul de l'arme
        if self.gun_recoil > 0:
            self.gun_recoil -= dt * 0.15  # Retour progressif
            if self.gun_recoil < 0:
                self.gun_recoil = 0

    def shoot(self):
        # Déclencher le recul de l'arme
        self.gun_recoil = 40  # Pixels de recul vers le haut

        # Jouer le son de tir
        if self.shotgun_sound:
            self.shotgun_sound.play()

        target = self.targets[self.current_target_index]
        tx, ty, tw, th = target.rect

        if self.sight.is_on_target(target):
            target.state = TargetState.HIT
            self.targets_hit += 1
            self.world.score += settings.TARGET_HIT_BONUS
            self.floating_texts.append({
                'text': f"+{settings.TARGET_HIT_BONUS}",
                'x': tx + tw // 2,
                'y': ty - 20,
                'color': (80, 220, 80),
                'alpha': 255,
                'scale': 1.2
            })
            self.flash_color = (0, 255, 0)
            self.flash_alpha = 80
        else:
            target.state = TargetState.MISSED
            self.flash_color = (255, 0, 0)
            self.flash_alpha = 100

        self.current_target_index += 1
        self.shots_remaining -= 1

        if self.shots_remaining <= 0:
            self.phase_complete = True
            if self.targets_hit == settings.NUM_TARGETS:
                self.flash_color = (255, 215, 0)
                self.flash_alpha = 150

    def render(self, screen):
        self.renderer.draw_shooting_background(screen)
        self.renderer.draw_targets(screen, self.targets)
        if not self.phase_complete:
            self.renderer.draw_sight(screen, self.sight)

        # Dessiner l'arme avec effet de recul
        self.renderer.draw_gun(screen, self.sight, self.gun_recoil)

        self.renderer.draw_shooting_ui(screen, self.shots_remaining, self.targets_hit, self.world.score, self.player.lives)

        self.renderer.draw_floating_text(screen, self.floating_texts)
        if self.flash_alpha > 0:
            self.renderer.draw_flash(screen, self.flash_color, self.flash_alpha)

        if self.phase_complete:
            if self.targets_hit == settings.NUM_TARGETS:
                msg = f"PARFAIT ! {self.targets_hit}/{settings.NUM_TARGETS} (+1 vie)"
                color = (255, 215, 0)
            elif self.targets_hit >= settings.MIN_TARGETS_TO_HIT:
                msg = f"Bien ! {self.targets_hit}/{settings.NUM_TARGETS} cibles"
                color = (60, 180, 60)
            else:
                msg = f"Raté ! {self.targets_hit}/{settings.NUM_TARGETS} (-1 vie)"
                color = (200, 60, 60)
            text = self.renderer.font_big.render(msg, True, color)
            screen.blit(text, (settings.WIDTH // 2 - text.get_width() // 2, settings.HEIGHT - 180))


class GameOverScene(Scene):
    def __init__(self, game, score, medal_score=0, distance=0):
        super().__init__(game)
        self.score = score
        self.medal_score = medal_score
        self.distance = distance
        self.input = InputController()
        self.renderer = Renderer()
        self.animation_time = 0
        self.can_restart = False

        self.best_score = self._load_best_score()
        if score > self.best_score:
            self._save_best_score(score)
            self.best_score = score

    def _load_best_score(self):
        try:
            with open(settings.ASSETS_DIR / "best_score.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0

    def _save_best_score(self, score):
        try:
            with open(settings.ASSETS_DIR / "best_score.txt", "w") as f:
                f.write(str(score))
        except:
            pass

    def handle_event(self, event):
        self.input.handle_event(event)

    def update(self, dt):
        self.animation_time += dt / 1000
        if self.animation_time >= 1.5:
            self.can_restart = True

        left, right, jump, start = self.input.consume()
        if self.can_restart and (start or jump):
            Renderer.reset_background_index()
            self.game.change_scene(CountdownScene(self.game, with_start=True))

    def render(self, screen):
        self.renderer.draw_background(screen)
        progress = min(1.0, self.animation_time / 1.5)
        self.renderer.draw_game_over(screen, self.score, self.medal_score, self.distance, self.best_score, progress)


# Alias pour compatibilité
PlayScene = SkiScene
