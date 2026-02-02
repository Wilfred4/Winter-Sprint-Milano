import random

from game.core import settings
from game.models.entities import Medal, Obstacle


class World:
    def __init__(self):
        self.obstacles = []
        self.medals = []
        self.score = 0
        self.medal_score = 0
        self.distance = 0.0
        self.speed = settings.BASE_SCROLL_SPEED
        self.time_since_spawn = 0.0
        self.next_spawn = settings.SPAWN_INTERVAL
        self.time_since_medal = 0.0
        self.next_medal = settings.MEDAL_SPAWN_INTERVAL

    def reset(self):
        self.__init__()

    def update(self, dt_ms):
        self.distance += dt_ms * 0.001
        self.speed = settings.BASE_SCROLL_SPEED + self.distance * settings.SPEED_GROWTH * 1000

        self.time_since_spawn += dt_ms
        if self.time_since_spawn >= self.next_spawn:
            self.spawn_obstacle()
            self.time_since_spawn = 0.0
            jitter = random.randint(-settings.SPAWN_JITTER, settings.SPAWN_JITTER)
            self.next_spawn = max(220, settings.SPAWN_INTERVAL + jitter)

        self.time_since_medal += dt_ms
        if self.time_since_medal >= self.next_medal:
            self.spawn_medal()
            self.time_since_medal = 0.0
            jitter = random.randint(-settings.MEDAL_SPAWN_JITTER, settings.MEDAL_SPAWN_JITTER)
            self.next_medal = max(400, settings.MEDAL_SPAWN_INTERVAL + jitter)

        for obstacle in self.obstacles:
            obstacle.update(self.speed)
        for medal in self.medals:
            medal.update(self.speed)

        self.obstacles = [o for o in self.obstacles if o.y - o.height < settings.HEIGHT + 40]
        self.medals = [m for m in self.medals if m.y - m.height < settings.HEIGHT + 40]

    def spawn_obstacle(self):
        lane = random.randint(0, settings.LANES - 1)
        y = -random.randint(40, 200)
        if not self._is_obstacle_spawn_clear(lane, y):
            return
        self.obstacles.append(Obstacle(lane=lane, y=y))

    def _is_obstacle_spawn_clear(self, lane, y):
        # prevent side-by-side "walls" that block the player
        min_gap = settings.OBSTACLE_SIZE[1] + 50
        for obstacle in self.obstacles:
            if abs(obstacle.y - y) < min_gap:
                return False
        return True

    def spawn_medal(self):
        lane = random.randint(0, settings.LANES - 1)
        y = -random.randint(60, 240)
        if not self._is_medal_lane_clear(lane, y):
            return
        kinds = list(settings.MEDAL_WEIGHTS.keys())
        weights = list(settings.MEDAL_WEIGHTS.values())
        kind = random.choices(kinds, weights=weights, k=1)[0]
        self.medals.append(Medal(kind=kind, lane=lane, y=y))

    def _is_medal_lane_clear(self, lane, y):
        min_gap = settings.OBSTACLE_SIZE[1] + settings.MEDAL_SIZE[1] + 40
        for obstacle in self.obstacles:
            if obstacle.lane != lane:
                continue
            if abs(obstacle.y - y) < min_gap:
                return False
        return True
