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

        # Timers pour les spawns
        self.time_since_spawn = 0.0
        self.next_spawn = settings.SPAWN_INTERVAL
        self.time_since_medal = 0.0
        self.next_medal = settings.MEDAL_SPAWN_INTERVAL

        # Timer pour les glaçons (spawn séparé)
        self.time_since_icicle = 0.0
        self.next_icicle = settings.ICICLE_SPAWN_INTERVAL

    def reset(self):
        self.__init__()

    def update(self, dt_ms):
        self.distance += dt_ms * 0.001
        # Vitesse progressive
        self.speed = min(
            settings.MAX_SCROLL_SPEED,
            settings.BASE_SCROLL_SPEED + self.distance * settings.SPEED_GROWTH
        )

        # Spawn des arbres
        self.time_since_spawn += dt_ms
        if self.time_since_spawn >= self.next_spawn:
            self.spawn_obstacle("tree")
            self.time_since_spawn = 0.0
            variation = random.randint(-settings.SPAWN_VARIATION, settings.SPAWN_VARIATION)
            self.next_spawn = max(220, settings.SPAWN_INTERVAL + variation)

        # Spawn des glaçons (moins fréquent)
        self.time_since_icicle += dt_ms
        if self.time_since_icicle >= self.next_icicle:
            self.spawn_obstacle("icicle")
            self.time_since_icicle = 0.0
            variation = random.randint(-settings.ICICLE_SPAWN_VARIATION, settings.ICICLE_SPAWN_VARIATION)
            self.next_icicle = max(1500, settings.ICICLE_SPAWN_INTERVAL + variation)

        # Spawn des médailles
        self.time_since_medal += dt_ms
        if self.time_since_medal >= self.next_medal:
            self.spawn_medal()
            self.time_since_medal = 0.0
            variation = random.randint(-settings.MEDAL_SPAWN_VARIATION, settings.MEDAL_SPAWN_VARIATION)
            self.next_medal = max(400, settings.MEDAL_SPAWN_INTERVAL + variation)

        # Mise à jour des positions
        for obstacle in self.obstacles:
            obstacle.update(self.speed)
        for medal in self.medals:
            medal.update(self.speed)

        # Nettoyer les objets hors écran
        self.obstacles = [o for o in self.obstacles if o.y - o.height < settings.HEIGHT + 40]
        self.medals = [m for m in self.medals if m.y - m.height < settings.HEIGHT + 40]

    def spawn_obstacle(self, obstacle_type="tree"):
        lane = random.randint(0, settings.LANES - 1)
        y = -random.randint(40, 200)
        if not self._is_obstacle_spawn_clear(lane, y):
            return
        self.obstacles.append(Obstacle(lane=lane, y=y, obstacle_type=obstacle_type))

    def _is_obstacle_spawn_clear(self, lane, y):
        # Eviter les murs infranchissables
        min_gap = settings.OBSTACLE_MIN_GAP
        for obstacle in self.obstacles:
            if abs(obstacle.y - y) < min_gap and abs(obstacle.lane - lane) <= 1:
                return False
        for medal in self.medals:
            if abs(medal.y - y) < settings.MEDAL_MIN_GAP and abs(medal.lane - lane) <= 1:
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
        min_gap = settings.MEDAL_MIN_GAP
        # Permet ne pas faire apparaitre au dessus d'un obstacle
        for obstacle in self.obstacles:
            if abs(obstacle.y - y) < min_gap and abs(obstacle.lane - lane) <= 1:
                return False
        # Permet de ne pas faire apparaitre plusieurs médailles côte à côte
        for medal in self.medals:
            if abs(medal.y - y) < min_gap and abs(medal.lane - lane) <= 1:
                return False
        return True
