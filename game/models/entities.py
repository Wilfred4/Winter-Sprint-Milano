from dataclasses import dataclass

from game.core import settings


def lane_x(lane_index):
    lane_width = (settings.WIDTH - 2 * settings.LANE_PADDING) // settings.LANES
    return settings.LANE_PADDING + lane_width * lane_index + lane_width // 2


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
        # vertical movement
        if not self.on_ground:
            self.velocity_y += settings.GRAVITY
            self.y += self.velocity_y
            if self.y >= settings.PLAYER_Y:
                self.y = settings.PLAYER_Y
                self.velocity_y = 0.0
                self.on_ground = True

        # smooth horizontal slide toward target lane
        target_x = float(lane_x(self.target_lane))
        delta = target_x - self.x
        max_step = settings.HORIZONTAL_SPEED * dt_sec
        step = max(-max_step, min(max_step, delta))
        self.x += step
        self.velocity_x = step / dt_sec if dt_sec > 0 else 0.0

        # tilt based on horizontal velocity
        self.tilt = max(-12.0, min(12.0, -self.velocity_x * settings.TILT_FACTOR))

    @property
    def rect(self):
        x = int(self.x) - self.width // 2
        y = int(self.y) - self.height
        return (x, y, self.width, self.height)


@dataclass
class Obstacle:
    lane: int
    y: float
    width: int = settings.OBSTACLE_SIZE[0]
    height: int = settings.OBSTACLE_SIZE[1]
    passed: bool = False

    def update(self, speed):
        self.y += speed

    @property
    def rect(self):
        x = lane_x(self.lane) - self.width // 2
        y = int(self.y) - self.height
        return (x, y, self.width, self.height)


@dataclass
class Medal:
    kind: str
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
