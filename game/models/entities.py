from dataclasses import dataclass
from enum import Enum

from game.core import settings


def lane_x(lane_index):
    """Retourne la position X du centre d'une voie."""
    lane_width = (settings.WIDTH - 2 * settings.LANE_PADDING) // settings.LANES
    return settings.LANE_PADDING + lane_width * lane_index + lane_width // 2


class TargetState(Enum):
    NORMAL = "normal"
    HIT = "hit"
    MISSED = "missed"


@dataclass
class Player:
    lane: int = 1
    target_lane: int = 1
    y: float = settings.PLAYER_Y
    width: int = settings.PLAYER_SIZE[0]
    height: int = settings.PLAYER_SIZE[1]
    velocity_y: float = 0.0
    on_ground: bool = True
    x: float = 0.0
    tilt: float = 0.0
    velocity_x: float = 0.0
    lives: int = settings.PLAYER_START_LIVES
    invincible_timer: float = 0.0

    def __post_init__(self):
        self.x = float(lane_x(self.lane))

    def move_left(self):
        self.target_lane = max(0, self.target_lane - 1)

    def move_right(self):
        self.target_lane = min(settings.LANES - 1, self.target_lane + 1)

    def jump(self):
        if self.on_ground:
            self.velocity_y = settings.JUMP_VELOCITY
            self.on_ground = False

    def update(self, dt):
        dt_sec = max(0.0, dt / 1000.0)

        # Timer invincibilité
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        # Saut / gravité
        if not self.on_ground:
            self.velocity_y += settings.GRAVITY
            self.y += self.velocity_y
            if self.y >= settings.PLAYER_Y:
                self.y = settings.PLAYER_Y
                self.velocity_y = 0.0
                self.on_ground = True

        # Déplacement horizontal fluide vers la voie cible
        target_x = float(lane_x(self.target_lane))
        delta = target_x - self.x
        max_step = settings.HORIZONTAL_SPEED * dt_sec
        step = max(-max_step, min(max_step, delta))
        self.x += step
        self.velocity_x = step / dt_sec if dt_sec > 0 else 0.0

        # Inclinaison du personnage
        self.tilt = max(-12.0, min(12.0, -self.velocity_x * settings.TILT_FACTOR))

    def take_damage(self):
        """Retourne True si le joueur est mort."""
        if self.invincible_timer <= 0:
            self.lives -= 1
            self.invincible_timer = settings.PLAYER_INVINCIBILITY_MS
            return self.lives < 0
        return False

    def is_invincible(self):
        return self.invincible_timer > 0

    @property
    def is_dead(self):
        return self.lives < 0

    @property
    def rect(self):
        x = int(self.x) - self.width // 2
        y = int(self.y) - self.height
        return (x, y, self.width, self.height)


@dataclass
class Obstacle:
    lane: int
    y: float
    obstacle_type: str = "tree"  # "tree" ou "icicle"
    width: int = None
    height: int = None
    passed: bool = False

    def __post_init__(self):
        # Taille selon le type d'obstacle
        if self.obstacle_type == "icicle":
            self.width = self.width or settings.ICICLE_SIZE[0]
            self.height = self.height or settings.ICICLE_SIZE[1]
        else:
            self.width = self.width or settings.OBSTACLE_SIZE[0]
            self.height = self.height or settings.OBSTACLE_SIZE[1]

    def update(self, speed):
        self.y += speed

    @property
    def rect(self):
        x = lane_x(self.lane) - self.width // 2
        y = int(self.y) - self.height
        return (x, y, self.width, self.height)


@dataclass
class Medal:
    kind: str  # bronze, silver, gold
    lane: int
    y: float
    width: int = settings.MEDAL_SIZE[0]
    height: int = settings.MEDAL_SIZE[1]

    def update(self, speed):
        self.y += speed

    @property
    def rect(self):
        x = lane_x(self.lane) - self.width // 2
        y = int(self.y) - self.height
        return (x, y, self.width, self.height)


@dataclass
class Target:
    """Cible pour la phase de tir."""
    x: float
    y: float = settings.TARGET_Y
    width: int = settings.TARGET_SIZE[0]
    height: int = settings.TARGET_SIZE[1]
    state: TargetState = TargetState.NORMAL

    @property
    def center_x(self):
        return self.x + self.width // 2

    @property
    def rect(self):
        return (int(self.x), int(self.y), self.width, self.height)


@dataclass
class Sight:
    """Viseur qui oscille pour la phase de tir."""
    x: float = settings.SIGHT_MIN_X
    y: float = settings.SIGHT_Y
    width: int = settings.SIGHT_SIZE[0]
    height: int = settings.SIGHT_SIZE[1]
    direction: int = 1  # 1 = droite, -1 = gauche

    def update(self):
        self.x += settings.SIGHT_SPEED * self.direction

        # Rebondir aux bords
        if self.x >= settings.SIGHT_MAX_X:
            self.x = settings.SIGHT_MAX_X
            self.direction = -1
        elif self.x <= settings.SIGHT_MIN_X:
            self.x = settings.SIGHT_MIN_X
            self.direction = 1

    @property
    def center_x(self):
        return self.x + self.width // 2

    def is_on_target(self, target):
        return abs(self.center_x - target.center_x) <= settings.TARGET_TOLERANCE


# Hockey

@dataclass
class HockeyPlayer:
    x: float
    y: float
    width: int = settings.HOCKEY_PLAYER_SIZE[0]
    height: int = settings.HOCKEY_PLAYER_SIZE[1]

    @property
    def rect(self):
        return (
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height
        )

    @property
    def center(self):
        return (self.x, self.y)


@dataclass
class Puck:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: int = settings.HOCKEY_PUCK_RADIUS

    def update(self, dt_sec):
        self.x += self.vx * dt_sec
        self.y += self.vy * dt_sec

        # Friction
        decay = max(0.0, 1.0 - settings.HOCKEY_PUCK_FRICTION * dt_sec)
        self.vx *= decay
        self.vy *= decay

        # Limiter la vitesse max
        speed = (self.vx ** 2 + self.vy ** 2) ** 0.5
        if speed > settings.HOCKEY_PUCK_MAX_SPEED:
            scale = settings.HOCKEY_PUCK_MAX_SPEED / speed
            self.vx *= scale
            self.vy *= scale

        # Stop les micro-mouvements
        if abs(self.vx) < settings.HOCKEY_PUCK_MIN_VELOCITY:
            self.vx = 0
        if abs(self.vy) < settings.HOCKEY_PUCK_MIN_VELOCITY:
            self.vy = 0
