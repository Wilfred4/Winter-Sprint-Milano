from pathlib import Path

# === ÉCRAN ===
WIDTH = 1920
HEIGHT = 1080
FPS = 60
FULLSCREEN = True  # Mettre True pour plein écran

# === PHASE SKI ===
LANES = 3
LANE_PADDING = 360  # Marge sur les côtés (proportionnel à la largeur)
PLAYER_Y = HEIGHT - 150  # Position Y du joueur
PLAYER_SIZE = (120, 150)  # Taille de la hitbox du joueur
PLAYER_RENDER_HEIGHT = 180  # Hauteur de rendu du joueur
OBSTACLE_SIZE = (100, 130)  # Taille des obstacles
MEDAL_SIZE = (72, 72)  # Taille des médailles
OBSTACLE_MIN_GAP = 200  # Écart minimum entre obstacles
MEDAL_MIN_GAP = 250  # Écart minimum pour les médailles

# Physique
GRAVITY = 1.2
JUMP_VELOCITY = -22
HORIZONTAL_SPEED = 1400  # px/sec pour changement de couloir
TILT_FACTOR = 0.08

# Vitesse et spawn
BASE_SCROLL_SPEED = 4       # Vitesse de départ
MAX_SCROLL_SPEED = 15       # Vitesse maximale
SPEED_GROWTH = 0.08         # Augmentation de vitesse par seconde de jeu

SPAWN_INTERVAL = 800  # ms
SPAWN_JITTER = 250    # ms
MEDAL_SPAWN_INTERVAL = 1200  # ms
MEDAL_SPAWN_JITTER = 400     # ms

# Couleurs
BG_COLOR = (16, 22, 33)
ROAD_COLOR = (28, 36, 54)
LANE_LINE = (60, 74, 100)
PLAYER_COLOR = (240, 240, 250)
OBSTACLE_COLOR = (255, 140, 60)
UI_COLOR = (10, 12, 18)
UI_SHADOW = (255, 255, 255)

# === ASSETS ===
ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"
PLAYER_IMG = ASSETS_DIR / "player.png"
OBSTACLE_IMG = ASSETS_DIR / "sapin.png"
MENU_BG_IMG = ASSETS_DIR / "accueil.png"

# === SYSTÈME DE MAPS ===
# Détection automatique des fonds de piste (fondrun*.png, fondrun*.jpg)
def get_background_images():
    "Récupère tous les fichiers de fond de piste disponibles"
    backgrounds = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        backgrounds.extend(ASSETS_DIR.glob(f'fondrun{ext}'))
        backgrounds.extend(ASSETS_DIR.glob(f'fondrun[0-9]{ext}'))
        backgrounds.extend(ASSETS_DIR.glob(f'fondrun[0-9][0-9]{ext}'))
    # Trier par nom pour un ordre cohérent
    backgrounds = sorted(set(backgrounds), key=lambda x: x.name)
    return backgrounds if backgrounds else [ASSETS_DIR / "fondrun.jpg"]

BACKGROUND_IMAGES = get_background_images()  # Liste de tous les fonds disponibles
BACKGROUND_IMG = BACKGROUND_IMAGES[0]  # Fond par défaut (premier de la liste)
MENU_BUTTON_IMG = ASSETS_DIR / "bouttonAccueil.png"
BUTTON_BIATHLON_IMG = ASSETS_DIR / "bouton_biathlon.png"
BUTTON_HOCKEY_IMG = ASSETS_DIR / "bouton_hockey.png"
BUTTON_QUIT_IMG = ASSETS_DIR / "bouton_quitter.png"
BUTTON_SETTINGS_IMG = ASSETS_DIR / "boutton_settings.png"
BUTTON_LEADERBOARD_IMG = ASSETS_DIR / "boutton_leaderboard.png"
HEART_IMG = ASSETS_DIR / "couer.png"
HEART_SIZE = (80, 68)  # Taille des cœurs (largeur, hauteur)
HEART_Y = 15  # Position Y des cœurs

# Sons
MUSIC_MENU = ASSETS_DIR / "son_menu.mp3"
MUSIC_GAME = ASSETS_DIR / "son_jeu.mp3"
SOUND_COIN = ASSETS_DIR / "coin.mp3"  # Son quand on récupère une médaille

MEDAL_BRONZE_IMG = ASSETS_DIR / "bronze.png"
MEDAL_SILVER_IMG = ASSETS_DIR / "argent.png"
MEDAL_GOLD_IMG = ASSETS_DIR / "or_1.png"

# Phase TIR - Images
SHOOTING_BG_IMG = ASSETS_DIR / "stand_tire.png"
TARGET_IMG = ASSETS_DIR / "cible.png"
SIGHT_IMG = ASSETS_DIR / "viseur.png"
GUN_IMG = ASSETS_DIR / "arme.png"
SOUND_SHOTGUN = ASSETS_DIR / "shotgun.mp3"

# Compteur (décompte)
COUNTDOWN_3_IMG = ASSETS_DIR / "compteur3.png"
COUNTDOWN_2_IMG = ASSETS_DIR / "compteur2.png"
COUNTDOWN_1_IMG = ASSETS_DIR / "compteur1.png"
COUNTDOWN_START_IMG = ASSETS_DIR / "compteur_start.png"

# Timing
COUNTDOWN_STEP_DURATION = 1000  # ms par étape (3, 2, 1, Start)
OBSTACLE_SPAWN_DELAY = 3000  # ms avant réapparition des obstacles après le tir
PRE_SHOOTING_CLEAR_TIME = 1000  # ms avant le décompte pour supprimer les obstacles

# === MÉDAILLES ===
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
SHOOTING_INTERVAL = 20000  # ms (20 secondes)
NUM_TARGETS = 5
TARGET_HIT_BONUS = 50
MIN_TARGETS_TO_HIT = 3
SHOOTING_TIME_LIMIT = 8000  # ms - Temps max pour tirer sur toutes les cibles (8 secondes)

# Position et taille des cibles
TARGET_Y = 280 #180  # Position Y des cibles
TARGET_SIZE = (150,135) #(100, 100)  # Taille des cibles

# Viseur
SIGHT_SIZE = (150, 130)  # Taille du viseur
SIGHT_MIN_X = 100  # Position X minimale
SIGHT_MAX_X = WIDTH - 220  # Position X maximale
SIGHT_SPEED = 12  # Vitesse du viseur
SIGHT_Y = TARGET_Y - 5  # Position Y (aligné avec les cibles)
TARGET_TOLERANCE = 60  # Zone de tolérance pour toucher

# Espacement des cibles (calculé automatiquement)
TARGET_SPACING = (WIDTH - 300) // (NUM_TARGETS - 1)

# Couleurs phase tir
TARGET_COLOR = (60, 60, 70)
TARGET_HIT_COLOR = (80, 200, 80)
TARGET_MISS_COLOR = (200, 80, 80)
SIGHT_COLOR = (255, 80, 80)
SHOOTING_BG_COLOR = (180, 200, 220)

# === HOCKEY ===
HOCKEY_RINK_MARGIN = 140
HOCKEY_GOAL_HEIGHT = 260
HOCKEY_PLAYER_SIZE = (70, 150)
HOCKEY_PUCK_RADIUS = 22
HOCKEY_PLAYER_SPEED = 900  # px/sec
HOCKEY_AI_SPEED = 760  # px/sec
HOCKEY_PUCK_SERVE_SPEED = 760  # px/sec
HOCKEY_PUCK_HIT_SPEED = 980  # px/sec
HOCKEY_PUCK_FRICTION = 0.85  # facteur de friction (0-1) par seconde
HOCKEY_PUCK_MAX_SPEED = 1500
HOCKEY_MATCH_TIME = 0  # ms (0 = pas de limite)
HOCKEY_MAX_SCORE = 3
HOCKEY_GOAL_PAUSE = 1200  # ms

HOCKEY_RINK_COLOR = (18, 32, 52)
HOCKEY_RINK_LINE = (220, 230, 240)
HOCKEY_GOAL_COLOR = (220, 80, 80)
HOCKEY_PLAYER_COLOR = (80, 180, 255)
HOCKEY_AI_COLOR = (255, 120, 120)
HOCKEY_PUCK_COLOR = (245, 245, 245)
