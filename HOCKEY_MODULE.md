# Module Hockey - Jeu 1v1 contre IA

## 📋 Fichiers à modifier

### 1. `game/core/settings.py`
Ajouter ces constantes à la fin du fichier :

```python
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
```

---

### 2. `game/models/entities.py`
Ajouter ces classes à la fin du fichier :

```python
# === HOCKEY ===

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
        decay = max(0.0, 1.0 - settings.HOCKEY_PUCK_FRICTION * dt_sec)
        self.vx *= decay
        self.vy *= decay

        # cap speed
        speed = (self.vx ** 2 + self.vy ** 2) ** 0.5
        if speed > settings.HOCKEY_PUCK_MAX_SPEED:
            scale = settings.HOCKEY_PUCK_MAX_SPEED / speed
            self.vx *= scale
            self.vy *= scale

        # stop micro jitter
        if abs(self.vx) < 6:
            self.vx = 0
        if abs(self.vy) < 6:
            self.vy = 0
```

---

### 3. `game/views/renderer.py`
Ajouter ces méthodes dans la classe `Renderer` :

```python
    # === HOCKEY ===

    def _load_hockey_player_image(self):
        if settings.PLAYER_IMG.exists():
            image = pygame.image.load(settings.PLAYER_IMG).convert_alpha()
            return image
        return None

    def draw_hockey_background(self, screen, rink_rect):
        screen.fill(settings.HOCKEY_RINK_COLOR)
        # glace bleutée
        pygame.draw.rect(screen, (200, 222, 242), rink_rect, border_radius=18)
        pygame.draw.rect(screen, (160, 190, 220), rink_rect, 6, border_radius=18)
        pygame.draw.rect(screen, settings.HOCKEY_RINK_LINE, rink_rect, 3, border_radius=18)

        # flocons légers
        for i in range(80):
            x = rink_rect.left + (i * 37) % max(1, rink_rect.width)
            y = rink_rect.top + (i * 53) % max(1, rink_rect.height)
            pygame.draw.circle(screen, (230, 240, 250), (x, y), 2)

        cx = rink_rect.centerx
        pygame.draw.line(screen, settings.HOCKEY_RINK_LINE,
                         (cx, rink_rect.top + 10), (cx, rink_rect.bottom - 10), 3)

        pygame.draw.circle(screen, settings.HOCKEY_RINK_LINE, rink_rect.center, 90, 3)

        goal_h = settings.HOCKEY_GOAL_HEIGHT
        goal_top = rink_rect.centery - goal_h // 2
        pygame.draw.rect(screen, settings.HOCKEY_GOAL_COLOR,
                         (rink_rect.left - 12, goal_top, 12, goal_h))
        pygame.draw.rect(screen, settings.HOCKEY_GOAL_COLOR,
                         (rink_rect.right, goal_top, 12, goal_h))

    def draw_hockey_player(self, screen, player, color, use_sprite=False):
        x, y, w, h = player.rect
        if use_sprite and self.hockey_player_image:
            img = self.hockey_player_image
            scale = h / img.get_height()
            new_w = max(1, int(img.get_width() * scale))
            new_h = max(1, int(img.get_height() * scale))
            sprite = pygame.transform.smoothscale(img, (new_w, new_h))
            sx = x + w // 2 - new_w // 2
            sy = y + h // 2 - new_h // 2
            screen.blit(sprite, (sx, sy))
            return
        pygame.draw.rect(screen, color, (x, y, w, h), border_radius=18)
        pygame.draw.rect(screen, (30, 30, 30), (x, y, w, h), 3, border_radius=18)

    def draw_hockey_puck(self, screen, puck, trail=None):
        if trail:
            for i, (tx, ty) in enumerate(trail):
                alpha = max(0, 200 - i * 12)
                radius = max(2, puck.radius - i // 3)
                surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                # halo bleu
                pygame.draw.circle(surf, (120, 170, 255, alpha), (radius + 2, radius + 2), radius + 1)
                # coeur plus clair
                pygame.draw.circle(surf, (200, 230, 255, alpha), (radius + 2, radius + 2), radius)
                screen.blit(surf, (int(tx - radius - 2), int(ty - radius - 2)))

        pygame.draw.circle(screen, settings.HOCKEY_PUCK_COLOR, (int(puck.x), int(puck.y)), puck.radius)
        pygame.draw.circle(screen, (30, 30, 30), (int(puck.x), int(puck.y)), puck.radius, 3)

    def draw_hockey_ui(self, screen, player_score, ai_score, time_left_ms):
        score_text = self.font_medium.render(f"JOUEUR {player_score}  -  {ai_score} IA", True, (245, 245, 250))
        screen.blit(score_text, (settings.WIDTH // 2 - score_text.get_width() // 2, 30))

        subtitle = self.font_small.render("Premier à 3 buts", True, (200, 210, 220))
        screen.blit(subtitle, (settings.WIDTH // 2 - subtitle.get_width() // 2, 80))

        hint = self.font_tiny.render("ZQSD / FLÈCHES pour bouger - M pour menu", True, (200, 200, 210))
        screen.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2, settings.HEIGHT - 60))

    def draw_hockey_goal_text(self, screen, text):
        msg = self.font_big.render(text, True, (255, 215, 0))
        screen.blit(msg, (settings.WIDTH // 2 - msg.get_width() // 2, settings.HEIGHT // 2 - 40))

    def draw_hockey_over(self, screen, result_text, player_score, ai_score):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.font_big.render(result_text, True, (255, 215, 0))
        screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, settings.HEIGHT // 2 - 120))

        score = self.font_medium.render(f"JOUEUR {player_score}  -  {ai_score} IA", True, (240, 240, 245))
        screen.blit(score, (settings.WIDTH // 2 - score.get_width() // 2, settings.HEIGHT // 2 - 30))

        replay = self.font_small.render("ENTER pour rejouer", True, (200, 200, 210))
        menu = self.font_small.render("M pour menu", True, (200, 200, 210))
        screen.blit(replay, (settings.WIDTH // 2 - replay.get_width() // 2, settings.HEIGHT // 2 + 60))
        screen.blit(menu, (settings.WIDTH // 2 - menu.get_width() // 2, settings.HEIGHT // 2 + 110))
```

**Dans `__init__`** ajouter :
```python
self.hockey_player_image = self._load_hockey_player_image()
```

---

### 4. `game/scenes/runner.py` (ou créer `game/scenes/hockey.py`)
Ajouter ces imports en haut :

```python
import math
import random
from game.models.entities import HockeyPlayer, Puck
```

Ajouter ces deux classes :

```python
class HockeyScene(Scene):
    """Mode Hockey 1v1 contre l'IA"""

    def __init__(self, game):
        super().__init__(game)
        self.renderer = Renderer()
        margin = settings.HOCKEY_RINK_MARGIN
        self.rink_rect = pygame.Rect(margin, margin, settings.WIDTH - 2 * margin, settings.HEIGHT - 2 * margin)

        cx, cy = self.rink_rect.center
        self.player = HockeyPlayer(self.rink_rect.left + 140, cy)
        self.ai = HockeyPlayer(self.rink_rect.right - 140, cy)
        self.puck = Puck(cx, cy)

        self.player_score = 0
        self.ai_score = 0
        self.time_left = settings.HOCKEY_MATCH_TIME
        self.goal_timer = 0
        self.goal_text = None
        self.serve_direction = random.choice([-1, 1])
        self.paused = False
        self.player_hit_cooldown = 0
        self.ai_hit_cooldown = 0
        self.ai_target_x = self.ai.x
        self.ai_target_y = self.ai.y
        self.puck_trail = []
        self.puck_trail_max = 18

        self._serve_puck()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            if event.key == pygame.K_m:
                self.game.change_scene(MenuScene(self.game))

    def update(self, dt):
        if self.paused:
            return

        if self.player_hit_cooldown > 0:
            self.player_hit_cooldown -= dt
        if self.ai_hit_cooldown > 0:
            self.ai_hit_cooldown -= dt

        if self.goal_timer > 0:
            self.goal_timer -= dt
            if self.goal_timer <= 0:
                self.goal_timer = 0
                self.goal_text = None
                self._serve_puck()
            return

        if settings.HOCKEY_MATCH_TIME > 0:
            self.time_left -= dt

        if self.player_score >= settings.HOCKEY_MAX_SCORE or self.ai_score >= settings.HOCKEY_MAX_SCORE:
            self.game.change_scene(HockeyOverScene(self.game, self.player_score, self.ai_score))
            return

        dt_sec = max(0.0, dt / 1000.0)
        player_vx, player_vy = self._update_player(dt_sec)
        ai_vx, ai_vy = self._update_ai(dt_sec)

        self.puck.update(dt_sec)

        self._update_trail()

        self._handle_wall_collisions()
        self._handle_player_collision(self.player, player_vx, player_vy)
        self._handle_player_collision(self.ai, ai_vx, ai_vy)
        self._check_goals()

    def _serve_puck(self):
        self.puck.x, self.puck.y = self.rink_rect.center
        self.puck.vx = self.serve_direction * settings.HOCKEY_PUCK_SERVE_SPEED
        self.puck.vy = random.uniform(-120, 120)

    def _update_player(self, dt_sec):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

        speed = settings.HOCKEY_PLAYER_SPEED
        move_x = dx * speed * dt_sec
        move_y = dy * speed * dt_sec

        self._move_in_bounds(self.player, move_x, move_y, left_side=None)
        return move_x / dt_sec if dt_sec > 0 else 0, move_y / dt_sec if dt_sec > 0 else 0

    def _update_ai(self, dt_sec):
        # IA type Air Hockey améliorée avec anticipation
        lookahead = 0.25
        predicted_x = self.puck.x + self.puck.vx * lookahead
        predicted_y = self.puck.y + self.puck.vy * lookahead
        
        # Stratégie selon la position du palet
        if self.puck.x > self.rink_rect.centerx + 100:
            # Palet proche : attaquer
            target_x = predicted_x - 90
            target_y = predicted_y
        elif self.puck.x > self.rink_rect.centerx - 200:
            # Palet au centre : intercepter
            target_x = self.rink_rect.centerx + 180
            target_y = predicted_y
        else:
            # Palet loin : défendre le but
            target_x = self.rink_rect.right - 160
            goal_center = self.rink_rect.centery
            target_y = self._lerp(goal_center, predicted_y, 0.7)

        # Limites Y
        target_y = max(self.rink_rect.top + 80, min(self.rink_rect.bottom - 80, target_y))

        # Lissage pour mouvement fluide
        self.ai_target_x = self._lerp(self.ai_target_x, target_x, 0.18)
        self.ai_target_y = self._lerp(self.ai_target_y, target_y, 0.18)

        dx = self.ai_target_x - self.ai.x
        dy = self.ai_target_y - self.ai.y

        dist = math.hypot(dx, dy)
        if dist < 4:
            return 0, 0

        dx /= dist
        dy /= dist

        speed = settings.HOCKEY_AI_SPEED
        move_x = dx * speed * dt_sec
        move_y = dy * speed * dt_sec

        self._move_in_bounds(self.ai, move_x, move_y, left_side=False)
        return move_x / dt_sec if dt_sec > 0 else 0, move_y / dt_sec if dt_sec > 0 else 0

    def _move_in_bounds(self, player, move_x, move_y, left_side=True):
        half_w = player.width / 2
        half_h = player.height / 2
        min_x = self.rink_rect.left + half_w
        max_x = self.rink_rect.right - half_w

        if left_side is True:
            max_x = self.rink_rect.centerx - 30 - half_w
        elif left_side is False:
            min_x = self.rink_rect.centerx + 30 + half_w

        min_y = self.rink_rect.top + half_h
        max_y = self.rink_rect.bottom - half_h

        player.x = max(min_x, min(max_x, player.x + move_x))
        player.y = max(min_y, min(max_y, player.y + move_y))

    def _handle_wall_collisions(self):
        left = self.rink_rect.left
        right = self.rink_rect.right
        top = self.rink_rect.top
        bottom = self.rink_rect.bottom
        r = self.puck.radius

        if self.puck.y - r <= top:
            self.puck.y = top + r
            self.puck.vy = abs(self.puck.vy)
        if self.puck.y + r >= bottom:
            self.puck.y = bottom - r
            self.puck.vy = -abs(self.puck.vy)

        goal_top = self.rink_rect.centery - settings.HOCKEY_GOAL_HEIGHT / 2
        goal_bottom = self.rink_rect.centery + settings.HOCKEY_GOAL_HEIGHT / 2

        if self.puck.x - r <= left and not (goal_top <= self.puck.y <= goal_bottom):
            self.puck.x = left + r
            self.puck.vx = abs(self.puck.vx)
        if self.puck.x + r >= right and not (goal_top <= self.puck.y <= goal_bottom):
            self.puck.x = right - r
            self.puck.vx = -abs(self.puck.vx)

        # Garder le palet dans la zone sans tremblements
        self.puck.x = max(left + r, min(right - r, self.puck.x))
        self.puck.y = max(top + r, min(bottom - r, self.puck.y))

        if abs(self.puck.vx) < 5:
            self.puck.vx = 0
        if abs(self.puck.vy) < 5:
            self.puck.vy = 0

    def _handle_player_collision(self, player, pvx, pvy):
        if player is self.player and self.player_hit_cooldown > 0:
            return
        if player is self.ai and self.ai_hit_cooldown > 0:
            return
        if not self._circle_rect_collision(self.puck, player):
            return

        px, py = player.center
        dx = self.puck.x - px
        dy = self.puck.y - py
        dist = math.hypot(dx, dy)
        if dist == 0:
            dx, dy = 1, 0
            dist = 1

        nx, ny = dx / dist, dy / dist
        push = (player.width * 0.5 + self.puck.radius + 4)
        self.puck.x = px + nx * push
        self.puck.y = py + ny * push

        # éviter les rebonds quand le palet s'éloigne déjà
        rel_vx = self.puck.vx - pvx
        rel_vy = self.puck.vy - pvy
        approach = rel_vx * nx + rel_vy * ny
        if approach > 0:
            self.puck.vx *= 0.65
            self.puck.vy *= 0.65
            return

        # Tir plus naturel avec direction du joueur
        hit_strength = settings.HOCKEY_PUCK_HIT_SPEED
        self.puck.vx = nx * hit_strength + pvx * 0.35
        self.puck.vy = ny * hit_strength + pvy * 0.35

        if player is self.player:
            self.player_hit_cooldown = 120
        else:
            self.ai_hit_cooldown = 120

    @staticmethod
    def _lerp(a, b, t):
        return a + (b - a) * t

    def _circle_rect_collision(self, puck, player):
        rx, ry, rw, rh = player.rect
        closest_x = max(rx, min(puck.x, rx + rw))
        closest_y = max(ry, min(puck.y, ry + rh))
        dx = puck.x - closest_x
        dy = puck.y - closest_y
        return (dx * dx + dy * dy) <= (puck.radius * puck.radius)

    def _check_goals(self):
        left = self.rink_rect.left
        right = self.rink_rect.right
        r = self.puck.radius
        goal_top = self.rink_rect.centery - settings.HOCKEY_GOAL_HEIGHT / 2
        goal_bottom = self.rink_rect.centery + settings.HOCKEY_GOAL_HEIGHT / 2

        if self.puck.x - r <= left and goal_top <= self.puck.y <= goal_bottom:
            self.ai_score += 1
            self.goal_text = "BUT IA !"
            self._start_goal_pause(serve_direction=-1)

        if self.puck.x + r >= right and goal_top <= self.puck.y <= goal_bottom:
            self.player_score += 1
            self.goal_text = "BUT JOUEUR !"
            self._start_goal_pause(serve_direction=1)

    def _start_goal_pause(self, serve_direction):
        self.goal_timer = settings.HOCKEY_GOAL_PAUSE
        self.serve_direction = serve_direction
        self.puck.vx = 0
        self.puck.vy = 0
        self.puck.x, self.puck.y = self.rink_rect.center
        self.puck_trail = []

    def _update_trail(self):
        speed = math.hypot(self.puck.vx, self.puck.vy)
        if speed > 30:
            self.puck_trail.insert(0, (self.puck.x, self.puck.y))
        if len(self.puck_trail) > self.puck_trail_max:
            self.puck_trail = self.puck_trail[: self.puck_trail_max]

    def render(self, screen):
        self.renderer.draw_hockey_background(screen, self.rink_rect)
        self.renderer.draw_hockey_player(screen, self.player, settings.HOCKEY_PLAYER_COLOR, use_sprite=True)
        self.renderer.draw_hockey_player(screen, self.ai, settings.HOCKEY_AI_COLOR)
        self.renderer.draw_hockey_puck(screen, self.puck, self.puck_trail)
        self.renderer.draw_hockey_ui(screen, self.player_score, self.ai_score, self.time_left)

        if self.goal_text:
            self.renderer.draw_hockey_goal_text(screen, self.goal_text)

        if self.paused:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            self.renderer.draw_title(screen, "Pause", "Echap pour reprendre")


class HockeyOverScene(Scene):
    def __init__(self, game, player_score, ai_score):
        super().__init__(game)
        self.player_score = player_score
        self.ai_score = ai_score
        self.renderer = Renderer()
        self.restart = False
        self.back_to_menu = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.restart = True
            if event.key == pygame.K_m:
                self.back_to_menu = True

    def update(self, dt):
        if self.restart:
            self.game.change_scene(HockeyScene(self.game))
        if self.back_to_menu:
            self.game.change_scene(MenuScene(self.game))

    def render(self, screen):
        if self.player_score > self.ai_score:
            result = "VICTOIRE !"
        elif self.player_score < self.ai_score:
            result = "DÉFAITE"
        else:
            result = "ÉGALITÉ"
        self.renderer.draw_hockey_over(screen, result, self.player_score, self.ai_score)
```

---

## 🎮 Lancer le mode Hockey

Depuis le menu, ajouter un bouton qui fait :
```python
self.game.change_scene(HockeyScene(self.game))
```

---

## ✨ Fonctionnalités

- ✅ **Physique réaliste** : Friction, rebonds, vitesse max
- ✅ **IA intelligente** : 3 modes (attaque/interception/défense) avec anticipation
- ✅ **Traînée visuelle** : Effet glisse sur glace
- ✅ **Terrain enneigé** : Glace bleutée avec flocons
- ✅ **Sprite joueur** : Utilise player.png avec ratio conservé
- ✅ **Premier à 3 buts** : Match sans limite de temps
- ✅ **Contrôles fluides** : ZQSD ou flèches, collision naturelle
- ✅ **Écran fin** : Victoire/Défaite/Égalité avec rejouer/menu

---

## 🎯 Contrôles

- **ZQSD / Flèches** : Déplacer le joueur
- **Echap** : Pause
- **M** : Retour menu
- **Enter** : Rejouer (écran de fin)

---

## 📝 Notes techniques

- Résolution : 1920x1080
- FPS : 60
- Architecture MVC respectée
- Pas de dépendances externes (seulement pygame)
- Code propre et commenté
