from pathlib import Path

# Ecran
WIDTH = 1920
HEIGHT = 1080
FPS = 60
FULLSCREEN = True

# Phase Ski
LANES = 3
LANE_PADDING = 360
PLAYER_Y = HEIGHT - 150
PLAYER_SIZE = (120, 150)
PLAYER_RENDER_HEIGHT = 180
OBSTACLE_SIZE = (100, 130)
MEDAL_SIZE = (72, 72)
OBSTACLE_MIN_GAP = 200
MEDAL_MIN_GAP = 250

# Physique
GRAVITY = 1.2
JUMP_VELOCITY = -22
HORIZONTAL_SPEED = 1400
TILT_FACTOR = 0.08
PLAYER_INVINCIBILITY_MS = 1500
PLAYER_START_LIVES = 0

# Vitesse et spawn
BASE_SCROLL_SPEED = 7          # Vitesse de départ (augmenter pour aller plus vite)
MAX_SCROLL_SPEED = 18          # Vitesse max
SPEED_GROWTH = 0.18            # Accélération progressive

SPAWN_INTERVAL = 700           # Intervalle spawn arbres (ms)
SPAWN_VARIATION = 200
MEDAL_SPAWN_INTERVAL = 1000
MEDAL_SPAWN_VARIATION = 300

# Glaçons
ICICLE_SPAWN_INTERVAL = 100   # Intervalle spawn des  glaçons
ICICLE_SPAWN_VARIATION = 800

# Couleurs
BG_COLOR = (16, 22, 33)
ROAD_COLOR = (28, 36, 54)
LANE_LINE = (60, 74, 100)
PLAYER_COLOR = (240, 240, 250)
OBSTACLE_COLOR = (255, 140, 60)
UI_COLOR = (10, 12, 18)
UI_SHADOW = (255, 255, 255)

# Assets
ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"
PLAYER_IMG = ASSETS_DIR / "player.png"
OBSTACLE_IMG = ASSETS_DIR / "sapin.png"
ICICLE_IMG = ASSETS_DIR / "glacons.png"       # Obstacle glaçon
ICICLE_SIZE = (170, 120)              # Taille des glaçons
MENU_BG_IMG = ASSETS_DIR / "accueil.png"

# Maps (detection auto des fondrun*.png/jpg)
def get_background_images():
    backgrounds = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        backgrounds.extend(ASSETS_DIR.glob(f'fondrun{ext}'))
        backgrounds.extend(ASSETS_DIR.glob(f'fondrun[0-9]{ext}'))
        backgrounds.extend(ASSETS_DIR.glob(f'fondrun[0-9][0-9]{ext}'))
    backgrounds = sorted(set(backgrounds), key=lambda x: x.name)
    return backgrounds if backgrounds else [ASSETS_DIR / "fondrun.jpg"]

BACKGROUND_IMAGES = get_background_images()
BACKGROUND_IMG = BACKGROUND_IMAGES[0]
MENU_BUTTON_IMG = ASSETS_DIR / "bouttonAccueil.png"
BUTTON_BIATHLON_IMG = ASSETS_DIR / "bouton_biathlon.png"
BUTTON_HOCKEY_IMG = ASSETS_DIR / "bouton_hockey.png"
BUTTON_QUIT_IMG = ASSETS_DIR / "bouton_quitter.png"
BUTTON_SETTINGS_IMG = ASSETS_DIR / "boutton_settings.png"
BUTTON_LEADERBOARD_IMG = ASSETS_DIR / "boutton_leaderboard.png"

# Taille des boutons du menu
MENU_BUTTON_WIDTH = 260    # Largeur des boutons
MENU_BUTTON_HEIGHT = 185   # Hauteur des boutons
MENU_BUTTON_SPACING = -100    # Espace entre les boutons (0 = collés)
MENU_BUTTON_BOTTOM_MARGIN = 3 # Marge en bas
HEART_IMG = ASSETS_DIR / "coeur.png"
HEART_SIZE = (80, 68)
HEART_Y = 15

# Sons
MUSIC_MENU = ASSETS_DIR / "son_menu.mp3"
MUSIC_GAME = ASSETS_DIR / "son_jeu.mp3"
SOUND_COIN = ASSETS_DIR / "coin.mp3"

MEDAL_BRONZE_IMG = ASSETS_DIR / "bronze.png"
MEDAL_SILVER_IMG = ASSETS_DIR / "argent.png"
MEDAL_GOLD_IMG = ASSETS_DIR / "or_1.png"

# Phase Tir - images
SHOOTING_BG_IMG = ASSETS_DIR / "stand_tire.png"
TARGET_IMG = ASSETS_DIR / "cible.png"
SIGHT_IMG = ASSETS_DIR / "viseur.png"
GUN_IMG = ASSETS_DIR / "arme.png"
SOUND_SHOTGUN = ASSETS_DIR / "shotgun.mp3"

# Compteur
COUNTDOWN_3_IMG = ASSETS_DIR / "compteur3.png"
COUNTDOWN_2_IMG = ASSETS_DIR / "compteur2.png"
COUNTDOWN_1_IMG = ASSETS_DIR / "compteur1.png"
COUNTDOWN_START_IMG = ASSETS_DIR / "compteur_start.png"

# Timing
COUNTDOWN_STEP_DURATION = 1000
OBSTACLE_SPAWN_DELAY = 3000
PRE_SHOOTING_CLEAR_TIME = 1000

# Medailles
MEDAL_POINTS = {
    "bronze": 1,
    "silver": 3,
    "gold": 5,
}
MEDAL_WEIGHTS = {
    "bronze": 70,
    "silver": 25,
    "gold": 5,
}

# Phase Tir
SHOOTING_INTERVAL = 12000      # Temps avant la phase de tir
NUM_TARGETS = 5
TARGET_HIT_BONUS = 50
MIN_TARGETS_TO_HIT = 3
SHOOTING_TIME_LIMIT = 8000

# Cibles
TARGET_Y = 280
TARGET_SIZE = (150, 135)

# Arme
GUN_WIDTH = 900                # Largeur de l'arme (augmenter pour élargir)
GUN_Y_OFFSET = 30              # Distance du bas de l'écran

# Viseur
SIGHT_SIZE = (150, 130)
SIGHT_MIN_X = 100
SIGHT_MAX_X = WIDTH - 220
SIGHT_SPEED = 12
SIGHT_Y = TARGET_Y - 5
TARGET_TOLERANCE = 60
TARGET_SPACING = (WIDTH - 300) // (NUM_TARGETS - 1)

# Couleurs phase tir
TARGET_COLOR = (60, 60, 70)
TARGET_HIT_COLOR = (80, 200, 80)
TARGET_MISS_COLOR = (200, 80, 80)
SIGHT_COLOR = (255, 80, 80)
SHOOTING_BG_COLOR = (180, 200, 220)

# Hockey
HOCKEY_RINK_MARGIN = 140
HOCKEY_GOAL_HEIGHT = 260
HOCKEY_PLAYER_SIZE = (70, 150)
HOCKEY_PUCK_RADIUS = 22
HOCKEY_PLAYER_SPEED = 900
HOCKEY_AI_SPEED = 760
HOCKEY_PUCK_SERVE_SPEED = 760
HOCKEY_PUCK_HIT_SPEED = 980
HOCKEY_PUCK_FRICTION = 0.85
HOCKEY_PUCK_MAX_SPEED = 1500
HOCKEY_MATCH_TIME = 0
HOCKEY_MAX_SCORE = 3
HOCKEY_GOAL_PAUSE = 1200

# Hockey IA
HOCKEY_AI_REACTION_SPEED = 380
HOCKEY_AI_SHOOT_POWER = 820
HOCKEY_AI_SHOOT_COOLDOWN_MS = 800
HOCKEY_SERVE_DELAY_MS = 700
HOCKEY_PUCK_MIN_VELOCITY = 6

# Hockey couleurs
HOCKEY_RINK_COLOR = (18, 32, 52)
HOCKEY_RINK_LINE = (220, 230, 240)
HOCKEY_GOAL_COLOR = (220, 80, 80)
HOCKEY_PLAYER_COLOR = (80, 180, 255)
HOCKEY_AI_COLOR = (255, 120, 120)
HOCKEY_PUCK_COLOR = (245, 245, 245)
