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
