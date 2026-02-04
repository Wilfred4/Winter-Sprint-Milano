from pathlib import Path

import pygame

from game.core import settings


class HockeySound:
    def __init__(self):
        self.enabled = False
        self.hit = None
        self.goal = None
        self.whistle = None
        self.crowd = None

        try:
            # Pré-init pour réduire la latence
            pygame.mixer.pre_init(44100, -16, 2, 256)
            pygame.mixer.init()
            self.enabled = True
        except Exception:
            self.enabled = False
            return

        sounds_dir = Path(settings.ASSETS_DIR) / "sounds"

        self.hit = self._load_sound(sounds_dir / "hit.mp3")
        self.goal = self._load_sound(sounds_dir / "goal.mp3")
        self.whistle = self._load_sound(sounds_dir / "whistle.mp3")
        self.crowd = self._load_sound(sounds_dir / "crowd.mp3")

        if self.crowd:
            try:
                self.crowd.set_volume(0.25)
                self.crowd.play(loops=-1)
            except Exception:
                pass

    def _load_sound(self, path: Path):
        if path.exists():
            try:
                snd = pygame.mixer.Sound(str(path))
                return snd
            except Exception:
                return None
        return None

    def play_hit(self):
        if self.enabled and self.hit:
            self.hit.play()

    def play_goal(self):
        if self.enabled and self.goal:
            self.goal.play()

    def play_whistle(self):
        if self.enabled and self.whistle:
            self.whistle.play()

    def stop(self):
        if self.enabled:
            try:
                pygame.mixer.stop()
            except Exception:
                pass
