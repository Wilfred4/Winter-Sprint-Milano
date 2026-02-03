from pathlib import Path

WIDTH = 960
HEIGHT = 720
FPS = 60
FULLSCREEN = False

LANES = 3
LANE_PADDING = 180
PLAYER_Y = HEIGHT - 90
PLAYER_SIZE = (70, 90)
PLAYER_RENDER_HEIGHT = 90
OBSTACLE_SIZE = (70, 90)
MEDAL_SIZE = (48, 48)
OBSTACLE_MIN_GAP = 140
MEDAL_MIN_GAP = 180

GRAVITY = 1.2
JUMP_VELOCITY = -18
HORIZONTAL_SPEED = 900  # px/sec for lane changes
TILT_FACTOR = 0.08      # deg per px/sec

BASE_SCROLL_SPEED = 4
SPEED_GROWTH = 0.0004

SPAWN_INTERVAL = 850  # ms
SPAWN_JITTER = 250    # ms
MEDAL_SPAWN_INTERVAL = 1200  # ms
MEDAL_SPAWN_JITTER = 400     # ms

BG_COLOR = (16, 22, 33)
ROAD_COLOR = (28, 36, 54)
LANE_LINE = (60, 74, 100)
PLAYER_COLOR = (240, 240, 250)
OBSTACLE_COLOR = (255, 140, 60)
UI_COLOR = (10, 12, 18)
UI_SHADOW = (255, 255, 255)

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"
PLAYER_IMG = ASSETS_DIR / "player.png"
OBSTACLE_IMG = ASSETS_DIR / "sapin.png"
BACKGROUND_IMG = ASSETS_DIR / "fondrun.jpg"
MENU_BG_IMG = ASSETS_DIR / "accueil.png"
MENU_BUTTON_IMG = ASSETS_DIR / "bouttonAccueil.png"
MEDAL_BRONZE_IMG = ASSETS_DIR / "bronze.png"
MEDAL_SILVER_IMG = ASSETS_DIR / "argent.png"
MEDAL_GOLD_IMG = ASSETS_DIR / "or_1.png"

# Phase TIR - Images
SHOOTING_BG_IMG = ASSETS_DIR / "stand_tire.png"
TARGET_IMG = ASSETS_DIR / "cible.png"
SIGHT_IMG = ASSETS_DIR / "viseur.png"

# Compteur (décompte)
COUNTDOWN_3_IMG = ASSETS_DIR / "compteur3.png"
COUNTDOWN_2_IMG = ASSETS_DIR / "compteur2.png"
COUNTDOWN_1_IMG = ASSETS_DIR / "compteur1.png"
COUNTDOWN_START_IMG = ASSETS_DIR / "compteur_start.png"

# Timing décompte
COUNTDOWN_STEP_DURATION = 1000  # ms par étape (3, 2, 1, Start)
OBSTACLE_SPAWN_DELAY = 1500  # ms avant que les obstacles réapparaissent après le tir

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

# === PHASE TIR ===
SHOOTING_INTERVAL = 20000  # ms (20 secondes) - temps entre chaque phase de tir
NUM_TARGETS = 5  # Nombre de cibles
TARGET_SIZE = (64, 64)  # Taille des cibles
TARGET_HIT_BONUS = 50  # Points bonus par cible touchée
MIN_TARGETS_TO_HIT = 3  # Minimum de cibles à toucher pour ne pas perdre de vie

# Positions des cibles (dans la bannière du stand)
TARGET_Y = 120  # Position Y des cibles
TARGET_SIZE = (70, 70)  # Taille des cibles

# Viseur (passe SUR les cibles)
SIGHT_SIZE = (80, 80)
SIGHT_MIN_X = 60  # Position X minimale du viseur
SIGHT_MAX_X = WIDTH - 140  # Position X maximale du viseur
SIGHT_SPEED = 8  # Pixels par frame
SIGHT_Y = TARGET_Y - 5  # Même niveau que les cibles
TARGET_TOLERANCE = 40  # Zone de tolérance pour toucher une cible (±pixels)
TARGET_SPACING = (WIDTH - 200) // (NUM_TARGETS - 1)  # Espacement entre cibles

# Couleurs phase tir
TARGET_COLOR = (60, 60, 70)
TARGET_HIT_COLOR = (80, 200, 80)
TARGET_MISS_COLOR = (200, 80, 80)
SIGHT_COLOR = (255, 80, 80)
SHOOTING_BG_COLOR = (180, 200, 220)
