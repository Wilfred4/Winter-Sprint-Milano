import pygame

from game.core import settings


class MusicManager:
    """Gère la musique du jeu."""

    _current_music = None

    @classmethod
    def play_menu_music(cls):
        if cls._current_music != "menu":
            pygame.mixer.music.stop()
            if settings.MUSIC_MENU.exists():
                pygame.mixer.music.load(str(settings.MUSIC_MENU))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                cls._current_music = "menu"

    @classmethod
    def play_game_music(cls):
        if cls._current_music != "game":
            pygame.mixer.music.stop()
            if settings.MUSIC_GAME.exists():
                pygame.mixer.music.load(str(settings.MUSIC_GAME))
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                cls._current_music = "game"

    @classmethod
    def stop(cls):
        pygame.mixer.music.stop()
        cls._current_music = None


class SoundManager:
    """Gère les effets sonores."""

    _coin_sound = None
    _initialized = False

    @classmethod
    def init(cls):
        if cls._initialized:
            return

        if settings.SOUND_COIN.exists():
            cls._coin_sound = pygame.mixer.Sound(str(settings.SOUND_COIN))
            cls._coin_sound.set_volume(0.6)
        else:
            # Fallback sur .wav si .mp3 pas trouvé
            coin_wav = settings.ASSETS_DIR / "coin.wav"
            if coin_wav.exists():
                cls._coin_sound = pygame.mixer.Sound(str(coin_wav))
                cls._coin_sound.set_volume(0.6)

        cls._initialized = True

    @classmethod
    def play_coin(cls):
        if cls._coin_sound:
            cls._coin_sound.play()
