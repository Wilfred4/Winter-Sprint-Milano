# 🎿 Biathlon Run - Cahier des Charges

> **Projet Piscine Python - ESIEE-iT**
> **Groupe 2** : Doryan, Wilfred-Raj, Younes, Yazid, Yassir
> **Thème** : Jeux Olympiques d'Hiver 2026 (Milan-Cortina)

---

## 🎮 Concept du jeu

**Biathlon Run** est un jeu combinant deux phases de gameplay inspirées du biathlon olympique :
1. **Phase SKI** : Course d'esquive style "Subway Surfers"
2. **Phase TIR** : Mini-jeu de précision avec timing

Le joueur alterne entre ces deux phases tout au long de la partie. Et le jeu ne s'arrête pas tant que le joueur a des vies.

---

## 🕹️ Règles du jeu

### Règles générales
- Le joueur commence avec **0 vies**
- Si le joueur percute un obstacle ou lors de la phase de tir, il réussi à tirer sur moins de 3 cibles alors il perd une vie. S'il commence avec aucune vie et qu'il percute ou tire sur moins de 3 cibles, la partie se termine.
- La partie se termine quand les vies tombent à 0
- Le but : parcourir la plus grande distance possible
- **Score** = distance parcourue + bonus des cibles touchées + médailles récupéré

### Phase SKI (Course)
- Le skieur avance automatiquement (le décor défile)
- **3 couloirs** : Gauche, Centre, Droite
- Le joueur change de couloir avec **← et →**
- Des obstacles apparaissent sur les couloirs
- **Collision avec obstacle** = -1 vie si 0 vie dès le début, il perd la partie.
- Tous les **20secondes** → passage en Phase TIR

### Phase TIR (Cibles)
- **5 cibles** alignées horizontalement
- Un **curseur/viseur** se déplace automatiquement de gauche à droite au dessus des cibles
- Le joueur appuie sur **ESPACE** pour tirer
- **Cible touchée** = +50 points bonus
- **Cible ratée** = -1 vie
- Après les 5 tirs → retour en Phase SKI et reprend d'où il était, avec la même distance et le même score

---

## 🎨 Éléments visuels

### Sprites nécessaires

| Sprite           | Description            | Taille suggérée |
| ---------------- | ---------------------- | --------------- |
| `skieur.png`     | Le personnage joueur   | 64x64 px        |
| `arbre.png`      | Obstacle sapin         | 48x80 px        |
| `rocher.png`     | Obstacle rocher        | 48x48 px        |
| `barriere.png`   | Obstacle barrière      | 80x48 px        |
| `cible.png`      | Cible de tir (normale) | 64x64 px        |
| `cible_hit.png`  | Cible touchée (verte)  | 64x64 px        |
| `cible_miss.png` | Cible ratée (rouge)    | 64x64 px        |
| `viseur.png`     | Curseur de visée       | 32x32 px        |
| `coeur.png`      | Icône vie              | 32x32 px        |

### Fonds d'écran

| Fond | Utilisation |
|------|-------------|
| `fond_ski.png` | Phase SKI - Piste enneigée (répétable verticalement) |
| `fond_tir.png` | Phase TIR - Stand de tir |

### Interface (UI)

- **Score** : En haut à gauche
- **Distance** : En haut au centre (ex: "750m")
- **Vies** : En haut à droite (3 cœurs)
- **Indicateur prochain tir** : compte à rebours à partir de 20 jusque 0 (il faut que le temps soit changeable)

---

## 🔊 Sons (optionnel mais valorisé)

| Son | Déclencheur |
|-----|-------------|
| `ski_ambient.wav` | Musique de fond phase SKI |
| `collision.wav` | Quand le skieur touche un obstacle |
| `tir.wav` | Quand le joueur appuie sur ESPACE |
| `cible_ok.wav` | Cible touchée |
| `cible_fail.wav` | Cible ratée |
| `gameover.wav` | Fin de partie |

---

## 📐 Spécifications techniques

### Fenêtre
- **Résolution** : 800 x 600 pixels
- **FPS** : 60 images/seconde

### Système de couloirs (Phase SKI)

```
|   GAUCHE   |   CENTRE   |   DROITE   |
|   x=133    |   x=400    |   x=667    |
|            |            |            |
|     🌲     |            |     🪨     |  <- Obstacles
|            |            |            |
|            |     ⛷️      |            |  <- Joueur (y fixe)
```

**Positions X des couloirs** :
- Gauche : `WIDTH // 6` = 133 px
- Centre : `WIDTH // 2` = 400 px
- Droite : `5 * WIDTH // 6` = 667 px

**Position Y du joueur** : fixe à `HEIGHT - 100` = 500 px

### Système de visée (Phase TIR)

```
    [CIB1] [CIB2] [CIB3] [CIB4] [CIB5]
              
         ◎ ──────────────────>
       (viseur qui se déplace)
```

- Le viseur part de `x=100` et va jusqu'à `x=700`
- Vitesse du viseur : 5-8 pixels par frame (ajustable)
- Quand ESPACE pressé : vérifier si viseur aligné avec une cible
- **Zone de tolérance** : ±30 pixels du centre de la cible

---

## 🔄 États du jeu

```
┌─────────┐
│  MENU   │ ──(ENTER)──> ┌─────────┐
└─────────┘              │   SKI   │ <───────────────┐
                         └────┬────┘                 │
                              │                      │
                         (500m atteint)              │
                              │                      │
                              v                      │
                         ┌─────────┐                 │
                         │   TIR   │ ──(5 tirs)──────┘
                         └────┬────┘
                              │
                         (vies = 0)
                              │
                              v
                         ┌──────────┐
                         │ GAMEOVER │ ──(R)──> MENU
                         └──────────┘
```

---

## ✅ Critères de validation

### Minimum requis (pour valider le projet)
- [x] Fenêtre Pygame fonctionnelle
- [x] Skieur qui change de couloir (3 positions)
- [x] Obstacles qui défilent
- [x] Collisions détectées
- [x] Phase de tir avec viseur mobile
- [x] Score affiché
- [ ] Système de vies
- [ ] Le jeu ne crashe pas

### Bonus (pour une meilleure note)
- [ ] Menu de démarrage
- [ ] Écran Game Over avec score final
- [ ] Sons
- [ ] Fond qui défile (scrolling)
- [ ] Difficulté progressive (vitesse augmente)
- [ ] Animation du skieur
- [ ] Sauvegarde du meilleur score

---

## 📁 Structure du projet

```
biathlon/
├── main.py              # Point d'entrée + boucle principale
├── settings.py          # Constantes (WIDTH, HEIGHT, FPS, couleurs)
├── sprites.py           # Classes Skieur, Obstacle, Cible, Viseur
└── assets/
    ├── images/
    │   ├── skieur.png
    │   ├── arbre.png
    │   ├── rocher.png
    │   ├── cible.png
    │   ├── viseur.png
    │   ├── coeur.png
    │   ├── fond_ski.png
    │   └── fond_tir.png
    └── sons/
        ├── tir.wav
        ├── hit.wav
        └── miss.wav
```

---

## 👥 Répartition des rôles


| Personne  | Responsabilité                                                         |
| --------- | ---------------------------------------------------------------------- |
| **Dev 1** | main.py + système d'états (menu → ski → tir → ski → ... → gameover)    |
| **Dev 2** | Phase ski complète (skieur, 3 couloirs, défilement, compteur distance) |
| **Dev 3** | Phase tir complète (curseur oscillant, cibles, détection Espace, vies) |
| Dev 4     | Obstacles + collisions + assets + sons + écrans (menu/gameover)        |


*Document créé le 2 février 2026*
