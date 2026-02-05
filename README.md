# Winter Sprint Milano

## Prerequisites
- Python 3.10+
- pygame

## Install
```powershell
python -m pip install pygame
```

## Run
```powershell
python index.py
```

## Controls
- Left / Right: changer de voie
- Space / Up: sauter
- Enter: start / restart
- Esc: quitter

### Hockey 1v1
- Flèches / ZQSD: bouger
- M: retour menu

## Structure (MVC)
- `game/models`: état et logique (player, obstacles, world)
- `game/views`: rendu (drawing)
- `game/controllers`: input et orchestration
- `game/scenes`: menu, jeu, game over
- `game/core`: loop, settings, utilities

Assets: le jeu utilise des formes dessinées en code pour fonctionner sans images. Vous pouvez remplacer par des PNG dans `assets/` et adapter `game/views/renderer.py`.
