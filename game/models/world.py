import random

from game.core import settings
from game.models.entities import Obstacle


class World:
    def __init__(self):
        self.obstacles = []
        self.score = 0
        self.distance = 0.0
        self.speed = settings.BASE_SCROLL_SPEED
        self.time_since_spawn = 0.0
        self.next_spawn = settings.SPAWN_INTERVAL

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

        for obstacle in self.obstacles:
            obstacle.update(self.speed)

        self.obstacles = [o for o in self.obstacles if o.y - o.height < settings.HEIGHT + 40]

    def spawn_obstacle(self):
        lane = random.randint(0, settings.LANES - 1)
        y = -random.randint(40, 200)
        self.obstacles.append(Obstacle(lane=lane, y=y))
