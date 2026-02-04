from dataclasses import dataclass

from game.core import settings


@dataclass
class HockeyPlayer:
    x: float
    y: float
    width: int = settings.HOCKEY_PLAYER_SIZE[0]
    height: int = settings.HOCKEY_PLAYER_SIZE[1]

    @property
    def rect(self):
        return (int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height)

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

    def update(self, dt_sec: float):
        self.x += self.vx * dt_sec
        self.y += self.vy * dt_sec

        # friction
        friction = 0.985
        self.vx *= friction
        self.vy *= friction

        # stop micro jitter
        if abs(self.vx) < 5:
            self.vx = 0
        if abs(self.vy) < 5:
            self.vy = 0
