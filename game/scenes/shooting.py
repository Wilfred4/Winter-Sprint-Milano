import pygame

from game.core import settings
from game.controllers.input import InputController
from game.models.entities import Target, Sight, TargetState
from game.scenes.base import Scene
from game.views.renderer import Renderer


class ShootingScene(Scene):
    """Phase de tir - toucher les 5 cibles."""

    def __init__(self, game, player, world):
        super().__init__(game)
        self.input = InputController()
        self.renderer = Renderer()
        self.player = player
        self.world = world

        # Créer les cibles (espacées sur l'écran)
        self.targets = []
        margin = 200
        total_width = settings.WIDTH - 2 * margin
        spacing = total_width // (settings.NUM_TARGETS - 1)
        for i in range(settings.NUM_TARGETS):
            x = margin + i * spacing - settings.TARGET_SIZE[0] // 2
            self.targets.append(Target(x=x))

        self.sight = Sight()

        self.current_target_index = 0
        self.shots_remaining = settings.NUM_TARGETS
        self.targets_hit = 0
        self.shot_cooldown = 0
        self.transition_timer = 0
        self.phase_complete = False

        # Timer
        self.time_remaining = settings.SHOOTING_TIME_LIMIT
        self.time_expired = False

        # Effets
        self.floating_texts = []
        self.flash_color = None
        self.flash_alpha = 0
        self.gun_recoil = 0

        # Son du tir
        self.shotgun_sound = None
        if settings.SOUND_SHOTGUN.exists():
            self.shotgun_sound = pygame.mixer.Sound(str(settings.SOUND_SHOTGUN))
            self.shotgun_sound.set_volume(0.5)

    def handle_event(self, event):
        self.input.handle_event(event)

    def update(self, dt):
        _, _, jump, _ = self.input.consume()

        self._update_effects(dt)

        if self.shot_cooldown > 0:
            self.shot_cooldown -= dt

        if self.phase_complete:
            self.transition_timer += dt
            if self.transition_timer >= 1500:
                self._finish_phase()
            return

        # Timer
        if self.time_remaining > 0:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.time_expired = True
                self.phase_complete = True
                self.flash_color = (255, 0, 0)
                self.flash_alpha = 150

        self.sight.update()

        # Tir
        if jump and self.shot_cooldown <= 0 and self.current_target_index < len(self.targets):
            self._shoot()
            self.shot_cooldown = 400

    def _finish_phase(self):
        from game.scenes.ski import SkiScene
        from game.scenes.gameover import GameOverScene

        # Pénalité si raté
        if self.time_expired or self.targets_hit < settings.MIN_TARGETS_TO_HIT:
            if self.player.take_damage():
                self.game.change_scene(GameOverScene(
                    self.game, self.world.score, self.world.medal_score, self.world.distance
                ))
                return
        # Bonus si tous touché
        elif self.targets_hit == settings.NUM_TARGETS and not self.time_expired:
            self.player.lives += 1

        self.renderer.next_background()
        self.game.change_scene(SkiScene(self.game, self.player, self.world, from_shooting=True))

    def _update_effects(self, dt):
        if self.flash_alpha > 0:
            self.flash_alpha -= dt * 0.3

        for t in self.floating_texts:
            t['y'] -= dt * 0.05
            t['alpha'] -= dt * 0.15
        self.floating_texts = [t for t in self.floating_texts if t['alpha'] > 0]

        if self.gun_recoil > 0:
            self.gun_recoil -= dt * 0.15
            if self.gun_recoil < 0:
                self.gun_recoil = 0

    def _shoot(self):
        self.gun_recoil = 40

        if self.shotgun_sound:
            self.shotgun_sound.play()

        target = self.targets[self.current_target_index]
        tx, ty, tw, th = target.rect

        if self.sight.is_on_target(target):
            # Touché !
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
            # Raté
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

        self.renderer.draw_gun(screen, self.sight, self.gun_recoil)
        self.renderer.draw_shooting_ui(
            screen, self.shots_remaining, self.targets_hit,
            self.world.score, self.player.lives
        )

        # Timer
        seconds = max(0, self.time_remaining / 1000)
        if seconds > 4:
            color = (80, 200, 80)
        elif seconds > 2:
            color = (255, 200, 60)
        else:
            color = (255, 60, 60)
        timer_text = self.renderer.font_big.render(f"{seconds:.1f}s", True, color)
        screen.blit(timer_text, (30, 80))  # En haut à gauche, sous le score

        self.renderer.draw_floating_text(screen, self.floating_texts)
        if self.flash_alpha > 0:
            self.renderer.draw_flash(screen, self.flash_color, self.flash_alpha)

        # Message de résultat
        if self.phase_complete:
            if self.time_expired:
                msg = f"TEMPS ECOULE ! {self.targets_hit}/{settings.NUM_TARGETS} (-1 vie)"
                color = (200, 60, 60)
            elif self.targets_hit == settings.NUM_TARGETS:
                msg = f"PARFAIT ! {self.targets_hit}/{settings.NUM_TARGETS} (+1 vie)"
                color = (255, 215, 0)
            elif self.targets_hit >= settings.MIN_TARGETS_TO_HIT:
                msg = f"Bien ! {self.targets_hit}/{settings.NUM_TARGETS} cibles"
                color = (60, 180, 60)
            else:
                msg = f"Rate ! {self.targets_hit}/{settings.NUM_TARGETS} (-1 vie)"
                color = (200, 60, 60)
            text = self.renderer.font_big.render(msg, True, color)
            screen.blit(text, (settings.WIDTH // 2 - text.get_width() // 2, settings.HEIGHT - 180))
