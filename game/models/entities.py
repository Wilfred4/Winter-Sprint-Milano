from dataclasses import dataclass

from game.core import settings


def lane_x(lane_index):
    lane_width = (settings.WIDTH - 2 * settings.LANE_PADDING) // settings.LANES
    return settings.LANE_PADDING + lane_width * lane_index + lane_width // 2


@dataclass
class Player:
    lane: int = 1
    y: float = settings.PLAYER_Y
    width: int = settings.PLAYER_SIZE[0]
    height: int = settings.PLAYER_SIZE[1]
    velocity_y: float = 0.0
    on_ground: bool = True

    def move_left(self):
        self.lane = max(0, self.lane - 1)

    def move_right(self):
        self.lane = min(settings.LANES - 1, self.lane + 1)

    def jump(self):
        if self.on_ground:
            self.velocity_y = settings.JUMP_VELOCITY
            self.on_ground = False

    def update(self, dt):
        if not self.on_ground:
            self.velocity_y += settings.GRAVITY
            self.y += self.velocity_y
            if self.y >= settings.PLAYER_Y:
                self.y = settings.PLAYER_Y
                self.velocity_y = 0.0
                self.on_ground = True

    @property
    def rect(self):
        x = lane_x(self.lane) - self.width // 2
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
